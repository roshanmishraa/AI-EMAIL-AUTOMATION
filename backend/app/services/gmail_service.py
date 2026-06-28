# ============================================================
# FILE:  backend/app/services/gmail_service.py
# CHANGE: fetch_unread_emails() mein actual attachment
#         extraction add kiya — filename + content save hota hai
# ============================================================

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import os
import json

from app.core.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


# -----------------------------
# GET GMAIL SERVICE
# -----------------------------
def get_gmail_service():
    token_path = settings.GMAIL_TOKEN_PATH

    if not os.path.exists(token_path):
        raise FileNotFoundError(
            "Gmail token missing. Run generate_gmail_token.py first."
        )

    with open(token_path) as f:
        token_data = json.load(f)

    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    return build("gmail", "v1", credentials=creds)


# -----------------------------
# HELPER: Recursively extract body + attachments from MIME parts
# Gmail messages can be nested (multipart/mixed → multipart/alternative → text/plain)
# -----------------------------
def _extract_parts(service, message_id: str, parts: list):
    """
    Returns:
        body (str)           — plain text body
        attachments (list)   — list of dicts: {filename, content, mime_type}
    """
    body        = ""
    attachments = []

    for part in parts:
        mime_type = part.get("mimeType", "")
        part_body = part.get("body", {})
        filename  = part.get("filename", "")

        # ── Nested multipart: recurse ──────────────────────────
        if mime_type.startswith("multipart/") and "parts" in part:
            nested_body, nested_att = _extract_parts(
                service, message_id, part["parts"]
            )
            if nested_body:
                body = body or nested_body   # first non-empty wins
            attachments.extend(nested_att)
            continue

        # ── Plain text body ────────────────────────────────────
        if mime_type == "text/plain" and not filename:
            data = part_body.get("data", "")
            if data:
                body = base64.urlsafe_b64decode(data).decode(
                    "utf-8", errors="ignore"
                )
            continue

        # ── Attachment ─────────────────────────────────────────
        # Criteria: has a filename (non-empty) OR body has an attachmentId
        attachment_id = part_body.get("attachmentId", "")
        if filename or attachment_id:
            content = ""

            if attachment_id:
                # Fetch attachment content from Gmail API
                try:
                    att_data = (
                        service.users()
                        .messages()
                        .attachments()
                        .get(userId="me", messageId=message_id, id=attachment_id)
                        .execute()
                    )
                    raw = att_data.get("data", "")
                    content = base64.urlsafe_b64decode(raw).decode(
                        "utf-8", errors="ignore"
                    )
                except Exception as e:
                    print(f"[Gmail] Attachment fetch failed: {e}")
                    content = ""

            elif part_body.get("data"):
                # Small inline attachment (data embedded directly)
                content = base64.urlsafe_b64decode(
                    part_body["data"]
                ).decode("utf-8", errors="ignore")

            attachments.append(
                {
                    "filename":  filename or f"attachment_{len(attachments)+1}",
                    "content":   content,
                    "mime_type": mime_type,
                }
            )

    return body, attachments


# -----------------------------
# FETCH UNREAD EMAILS
# -----------------------------
def fetch_unread_emails(max_results: int = 20):
    service = get_gmail_service()

    results = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX", "UNREAD"], maxResults=max_results)
        .execute()
    )

    messages = results.get("messages", [])
    emails   = []

    for msg in messages:
        msg_data = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="full")
            .execute()
        )

        payload = msg_data["payload"]
        headers = payload.get("headers", [])

        def get_header(name):
            for h in headers:
                if h["name"] == name:
                    return h["value"]
            return None

        subject   = get_header("Subject") or ""
        sender    = get_header("From") or ""
        thread_id = msg_data.get("threadId")

        # ── Extract body + attachments ───────────────────────────
        body        = ""
        attachments = []

        if "parts" in payload:
            body, attachments = _extract_parts(service, msg["id"], payload["parts"])
        else:
            # Single-part message (no nested parts)
            data = payload.get("body", {}).get("data", "")
            if data:
                body = base64.urlsafe_b64decode(data).decode(
                    "utf-8", errors="ignore"
                )

        # ── Build attachment summary ─────────────────────────────
        has_attachments   = len(attachments) > 0
        attachment_names  = json.dumps(
            [a["filename"] for a in attachments]
        ) if attachments else "[]"

        # ── Append attachment content to body (for AI processing) ─
        # This means the AI classifier + reply generator can also
        # "see" text inside attached .txt or .pdf files
        if attachments:
            extras = []
            for att in attachments:
                if att["content"].strip():
                    extras.append(
                        f"\n\n--- Attachment: {att['filename']} ---\n{att['content'][:2000]}"
                    )
            if extras:
                body += "".join(extras)

        emails.append(
            {
                "gmail_id":         msg["id"],
                "thread_id":        thread_id,
                "sender":           sender,
                "subject":          subject,
                "body":             body,
                "has_attachments":  has_attachments,
                "attachment_names": attachment_names,
            }
        )

    return emails


# -----------------------------
# SEND REPLY
# -----------------------------
def send_reply(thread_id: str, to: str, subject: str, body: str):
    service = get_gmail_service()

    message         = MIMEText(body)
    message["to"]   = to
    message["subject"] = "Re: " + subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service.users().messages().send(
            userId="me",
            body={"raw": raw_message, "threadId": thread_id},
        ).execute()
        return True
    except Exception as e:
        print("Send failed:", e)
        return False


# -----------------------------
# APPLY LABEL (AI-Processed)
# -----------------------------
def apply_label(message_id: str, label: str = "AI-Processed"):
    service = get_gmail_service()

    try:
        labels   = service.users().labels().list(userId="me").execute()
        label_id = None

        for l in labels.get("labels", []):
            if l["name"] == label:
                label_id = l["id"]
                break

        if not label_id:
            created = service.users().labels().create(
                userId="me",
                body={
                    "name":                  label,
                    "labelListVisibility":   "labelShow",
                    "messageListVisibility": "show",
                },
            ).execute()
            label_id = created["id"]

        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": [label_id]},
        ).execute()

        return True

    except Exception as e:
        print("Label error:", e)
        return False