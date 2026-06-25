# Gmail API wrapper — production-ready MVP version

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
# FETCH UNREAD EMAILS
# -----------------------------
def fetch_unread_emails(max_results: int = 20):
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "UNREAD"],
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])

    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        payload = msg_data["payload"]
        headers = payload.get("headers", [])

        def get_header(name):
            for h in headers:
                if h["name"] == name:
                    return h["value"]
            return None

        subject = get_header("Subject")
        sender = get_header("From")
        thread_id = msg_data.get("threadId")

        # extract body (simple version)
        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        else:
            data = payload["body"].get("data", "")
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        emails.append({
            "gmail_id": msg["id"],
            "thread_id": thread_id,
            "sender": sender,
            "subject": subject,
            "body": body
        })

    return emails


# -----------------------------
# SEND REPLY (IMPORTANT FIXED)
# -----------------------------
def send_reply(thread_id: str, to: str, subject: str, body: str):
    service = get_gmail_service()

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = "Re: " + subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service.users().messages().send(
            userId="me",
            body={
                "raw": raw_message,
                "threadId": thread_id
            }
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
        # get existing labels
        labels = service.users().labels().list(userId="me").execute()

        label_id = None

        for l in labels.get("labels", []):
            if l["name"] == label:
                label_id = l["id"]
                break

        # create label if not exists
        if not label_id:
            created = service.users().labels().create(
                userId="me",
                body={
                    "name": label,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show"
                }
            ).execute()

            label_id = created["id"]

        # apply label
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={
                "addLabelIds": [label_id]
            }
        ).execute()

        return True

    except Exception as e:
        print("Label error:", e)
        return False