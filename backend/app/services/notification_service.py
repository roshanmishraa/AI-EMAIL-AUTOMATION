import httpx
from app.core.config import settings


async def send_escalation_alert(email_id: int, reason: str):
    message = f"""
🚨 ESCALATION ALERT
Email ID: {email_id}
Reason: {reason}
"""

    if not settings.SLACK_WEBHOOK_URL:
        print(f"[SLACK STUB] {message}")
        return True

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            settings.SLACK_WEBHOOK_URL,
            json={"text": message}
        )
        return resp.status_code == 200