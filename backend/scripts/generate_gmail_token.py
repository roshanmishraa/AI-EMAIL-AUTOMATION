"""
Run ONCE to generate Gmail OAuth token.
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from app.core.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


def main():
    try:
        client_config = {
            "installed": {
                "client_id": settings.GMAIL_CLIENT_ID,
                "client_secret": settings.GMAIL_CLIENT_SECRET,
                "redirect_uris": [os.getenv("GMAIL_REDIRECT_URI")],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

        flow = InstalledAppFlow.from_client_config(
            client_config,
            SCOPES
        )

        creds = flow.run_local_server(port=0)

        os.makedirs(
            os.path.dirname(settings.GMAIL_TOKEN_PATH),
            exist_ok=True
        )

        with open(settings.GMAIL_TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

        print(f"✅ Token saved at: {settings.GMAIL_TOKEN_PATH}")

    except Exception as e:
        print(f"❌ OAuth failed: {e}")


if __name__ == "__main__":
    main()
