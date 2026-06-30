# ============================================================
# FILE:  backend/app/services/notification_service.py
# CHANGE: Slack ke saath ab agent ko email bhi jaata hai
#         jab bhi koi email escalate hoti hai
# FIX:    Hardcoded localhost:5173 → settings.FRONTEND_URL
#         (production deploy mein Slack/email links kaam karein,
#          sirf local dev mein hi localhost na point karein)
# ============================================================

import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from app.core.config import settings


# ──────────────────────────────────────────
# SLACK ALERT
# ──────────────────────────────────────────
async def _send_slack_alert(email_id: int, reason: str) -> bool:
    frontend_url = os.getenv("FRONTEND_URL") or "http://localhost:5173"
    message = f"""
🚨 ESCALATION ALERT
Email ID: {email_id}
Reason: {reason}
Dashboard: {frontend_url}/email/{email_id}
"""
    if not settings.SLACK_WEBHOOK_URL:
        print(f"[SLACK STUB] {message}")
        return True

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                settings.SLACK_WEBHOOK_URL,
                json={"text": message},
                timeout=5.0,
            )
            return resp.status_code == 200
    except Exception as e:
        print(f"[Notification] Slack failed: {e}")
        return False


# ──────────────────────────────────────────
# EMAIL PING
# Uses SMTP — works with Gmail App Password,
# SendGrid, or any SMTP relay
# ──────────────────────────────────────────
def _send_email_alert(email_id: int, reason: str) -> bool:
    if not settings.AGENT_EMAIL:
        print(f"[EMAIL STUB] Would email agent about escalation email_id={email_id}")
        return True

    if not settings.SMTP_USER or not settings.SMTP_PASS:
        print("[Notification] SMTP_USER or SMTP_PASS not configured — skipping email alert")
        return False

    frontend_url = os.getenv("FRONTEND_URL") or "http://localhost:5173"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[BeastLife Support] Escalation: Email #{email_id} needs review"
        msg["From"]    = settings.SMTP_USER
        msg["To"]      = settings.AGENT_EMAIL

        # Plain text body
        plain = f"""
Escalation Alert — Action Required

Email ID : {email_id}
Reason   : {reason}
Link     : {frontend_url}/email/{email_id}

Please review this email in the support dashboard.

— AI Email Automation System
"""
        # HTML body
        html = f"""
<html><body style="font-family:sans-serif;color:#111;">
  <div style="background:#fff3f3;border-left:4px solid #e53e3e;padding:16px 20px;margin-bottom:16px;border-radius:4px;">
    <strong style="color:#c53030;">🚨 Escalation Alert</strong>
  </div>
  <table style="border-collapse:collapse;width:100%;max-width:480px;">
    <tr><td style="padding:6px 0;color:#555;width:120px;">Email ID</td><td><strong>#{email_id}</strong></td></tr>
    <tr><td style="padding:6px 0;color:#555;">Reason</td><td><strong>{reason}</strong></td></tr>
  </table>
  <div style="margin-top:24px;">
    <a href="{frontend_url}/email/{email_id}"
       style="background:#3182ce;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:600;">
      Open in Dashboard
    </a>
  </div>
  <p style="color:#888;font-size:12px;margin-top:24px;">— AI Email Automation System</p>
</body></html>
"""
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail(settings.SMTP_USER, settings.AGENT_EMAIL, msg.as_string())

        print(f"[Notification] Email alert sent to {settings.AGENT_EMAIL} for email_id={email_id}")
        return True

    except Exception as e:
        print(f"[Notification] Email alert failed: {e}")
        return False


# ──────────────────────────────────────────
# MAIN — called from ai_processor.py
# ──────────────────────────────────────────
async def send_escalation_alert(email_id: int, reason: str):
    """
    Called by ai_processor when an email is escalated.
    Sends BOTH Slack webhook AND agent email ping.
    Non-blocking — failures are logged, not raised.
    """
    # 1. Slack
    await _send_slack_alert(email_id, reason)

    # 2. Email ping to agent (sync — wrapped in try/except)
    try:
        _send_email_alert(email_id, reason)
    except Exception as e:
        print(f"[Notification] Email ping error (non-critical): {e}")