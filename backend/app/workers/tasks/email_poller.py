# ============================================================
# FILE:  backend/app/workers/tasks/email_poller.py
# CHANGE: Email() object mein has_attachments + attachment_names
#         fields ab populate hote hain (lines marked NEW)
# ============================================================

import asyncio
import datetime

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from sqlalchemy import select

from app.models.email import Email, EmailStatus
from app.models.thread import EmailThread, ThreadStatus
from app.services.gmail_service import fetch_unread_emails, apply_label


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, name="app.workers.tasks.email_poller.fetch_new_emails_task")
def fetch_new_emails_task(self):
    """Fetch unread Gmail → save to DB → dispatch AI processor."""
    try:
        run_async(_fetch_and_save())
    except Exception as exc:
        print(f"[Poller] Task failed: {exc}")
        raise self.retry(exc=exc, countdown=30)


async def _fetch_and_save():
    # ── 1. Fetch from Gmail ──────────────────────────────
    try:
        raw_emails = fetch_unread_emails(max_results=20)
    except FileNotFoundError:
        print("[Poller] Gmail token missing — skipping poll")
        return
    except Exception as e:
        print(f"[Poller] Gmail fetch error: {e}")
        return

    if not raw_emails:
        print("[Poller] No new emails found")
        return

    print(f"[Poller] Found {len(raw_emails)} email(s) to process")

    async with AsyncSessionLocal() as db:
        new_email_ids = []

        for raw in raw_emails:
            gmail_id  = raw.get("gmail_id", "")
            thread_id = raw.get("thread_id", "")

            # ── 2. Skip if already saved ─────────────────
            existing = await db.execute(
                select(Email).where(Email.gmail_message_id == gmail_id)
            )
            if existing.scalar_one_or_none():
                continue

            # ── 3. Upsert EmailThread ────────────────────
            thread_result = await db.execute(
                select(EmailThread).where(EmailThread.gmail_thread_id == thread_id)
            )
            thread = thread_result.scalar_one_or_none()

            if thread:
                thread.message_count   = (thread.message_count or 0) + 1
                thread.last_message_at = datetime.datetime.utcnow()
            else:
                thread = EmailThread(
                    gmail_thread_id=thread_id,
                    last_message_at=datetime.datetime.utcnow(),
                    status=ThreadStatus.open,
                    message_count=1,
                    priority_level=0,
                )
                db.add(thread)

            # ── 4. Save Email ────────────────────────────
            email = Email(
                gmail_message_id = gmail_id,
                thread_id        = thread_id,
                sender           = raw.get("sender", ""),
                subject          = raw.get("subject", ""),
                body             = raw.get("body", ""),
                received_at      = datetime.datetime.utcnow(),
                status           = EmailStatus.new,
                # ── NEW: attachment fields ──────────────
                has_attachments  = raw.get("has_attachments", False),
                attachment_names = raw.get("attachment_names", "[]"),
            )
            db.add(email)
            await db.flush()   # get email.id

            new_email_ids.append(email.id)

            # ── 5. Apply Gmail label ─────────────────────
            try:
                apply_label(gmail_id, label="AI-Processed")
            except Exception as e:
                print(f"[Poller] Label apply failed for {gmail_id}: {e}")

        await db.commit()

    # ── 6. Dispatch AI pipeline for each new email ───────
    from app.workers.tasks.ai_processor import process_email_ai
    for eid in new_email_ids:
        process_email_ai.delay(eid)
        print(f"[Poller] Dispatched AI pipeline for email_id={eid}")

    print(f"[Poller] ✓ Saved {len(new_email_ids)} new email(s)")