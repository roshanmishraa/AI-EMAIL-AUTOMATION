# ============================================================
# FILE:  backend/app/services/gmail_service.py
# CHANGE: Multi-user OAuth support add kiya
#         - get_gmail_service() ab token dict accept karta hai
#         - get_oauth_flow() helper add kiya
#         - get_auth_url() add kiya (frontend ke liye)
#         - exchange_code_for_token() add kiya (callback ke liye)
#         - fetch_unread_emails() ab user_token parameter leta hai
#         - send_reply() ab user_token parameter leta hai
#         - apply_label() ab user_token parameter leta hai
#         - FIX: PKCE autogenerate_code_verifier=False — kyunki har
#           request pe naya Flow object banta hai, code_verifier
#           persist nahi hota, isliye token exchange "invalid_grant:
#           Missing code verifier" se fail ho raha tha. Confidential
#           client (client_secret hai) ke liye PKCE zaroori nahi hai.
# ============================================================

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
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
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]


# -----------------------------
# OAUTH FLOW HELPER
# -----------------------------
def get_oauth_flow() -> Flow:
    """
    Google OAuth2 Flow object banata hai.
    Client credentials .env se aate hain.
    """
    client_config = {
        "web": {
            "client_id":                   os.getenv("GMAIL_CLIENT_ID"),
            "client_secret":               os.getenv("GMAIL_CLIENT_SECRET"),
            "redirect_uris":               [os.getenv("GMAIL_REDIRECT_URI")],
            "auth_uri":                    "https://accounts.google.com/o/oauth2/auth",
            "token_uri":                   "https://oauth2.googleapis.com/token",
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=os.getenv("GMAIL_REDIRECT_URI"),
        autogenerate_code_verifier=False,   # ← FIX: PKCE disabled (confidential client, client_secret already present)
    )
    return flow


def get_auth_url() -> str:
    """
    Frontend ke liye Google OAuth URL generate karta hai.
    User is URL pe jaata hai → Google login karta hai → callback aata hai.
    """
    flow = get_oauth_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",      # refresh_token milega
        include_granted_scopes="true",
        prompt="consent",           # har baar consent screen dikhao (refresh token ke liye)
    )
    return auth_url


def exchange_code_for_token(code: str) -> dict:
    """
    Google se authorization code milta hai → access+refresh token exchange karta hai.
    Token dict return karta hai jo DB mein store hoga.
    """
    flow = get_oauth_flow()
    flow.fetch_token(code=code)
    creds = flow.credentials

    token_data = {
        "token":         creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri":     creds.token_uri,
        "client_id":     creds.client_id,
        "client_secret": creds.client_secret,
        "scopes":        list(creds.scopes) if creds.scopes else SCOPES,
    }
    return token_data


def get_user_email_from_token(token_data: dict) -> str:
    """
    Token se user ki Gmail address nikalta hai.
    DB mein user identify karne ke liye use hota hai.
    """
    creds   = Credentials.from_authorized_user_info(token_data, SCOPES)
    service = build("oauth2", "v2", credentials=creds)
    info    = service.userinfo().get().execute()
    return info.get("email", "")


# -----------------------------
# GET GMAIL SERVICE (MULTI-USER)
# -----------------------------
def get_gmail_service(user_token: dict = None):
    """
    Gmail API service object banata hai.

    Multi-user mode (RECOMMENDED):
        user_token = DB se laya hua token dict
        get_gmail_service(user_token=token_dict)

    Legacy fallback (single-user, file-based):
        get_gmail_service()  — purana gmail_token.json use karega
        (sirf backward compatibility ke liye, naye code mein use mat karo)
    """
    if user_token:
        # ── Multi-user path: token DB se aaya ──────────────────
        creds = Credentials.from_authorized_user_info(user_token, SCOPES)
    else:
        # ── Legacy fallback: file-based token ──────────────────
        token_path = settings.GMAIL_TOKEN_PATH
        if not os.path.exists(token_path):
            raise FileNotFoundError(
                "Gmail token missing. Run generate_gmail_token.py first "
                "OR use OAuth login flow."
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
        attachment_id = part_body.get("attachmentId", "")
        if filename or attachment_id:
            content = ""

            if attachment_id:
                try:
                    att_data = (
                        service.users()
                        .messages()
                        .attachments()
                        .get(userId="me", messageId=message_id, id=attachment_id)
                        .execute()
                    )
                    raw     = att_data.get("data", "")
                    content = base64.urlsafe_b64decode(raw).decode(
                        "utf-8", errors="ignore"
                    )
                except Exception as e:
                    print(f"[Gmail] Attachment fetch failed: {e}")
                    content = ""

            elif part_body.get("data"):
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
def fetch_unread_emails(max_results: int = 20, user_token: dict = None):
    """
    user_token: DB se laya hua token dict (multi-user).
                None hone pe legacy file-based token use hoga.
    """
    service = get_gmail_service(user_token=user_token)

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
            data = payload.get("body", {}).get("data", "")
            if data:
                body = base64.urlsafe_b64decode(data).decode(
                    "utf-8", errors="ignore"
                )

        # ── Build attachment summary ─────────────────────────────
        has_attachments  = len(attachments) > 0
        attachment_names = json.dumps(
            [a["filename"] for a in attachments]
        ) if attachments else "[]"

        # ── Append attachment content to body (for AI processing) ─
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
def send_reply(thread_id: str, to: str, subject: str, body: str, user_token: dict = None):
    """
    user_token: DB se laya hua token dict (multi-user).
                None hone pe legacy file-based token use hoga.
    """
    service = get_gmail_service(user_token=user_token)

    message            = MIMEText(body)
    message["to"]      = to
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
def apply_label(message_id: str, label: str = "AI-Processed", user_token: dict = None):
    """
    user_token: DB se laya hua token dict (multi-user).
                None hone pe legacy file-based token use hoga.
    """
    service = get_gmail_service(user_token=user_token)

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