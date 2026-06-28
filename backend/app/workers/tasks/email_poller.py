# ============================================================
# FILE:  backend/app/workers/tasks/email_poller.py
# CHANGE: Multi-user support add kiya
#         - Ab saare active users ke liye emails fetch hoti hain
#         - har user ka apna gmail_token use hota hai
#         - Email save hote waqt user_id bhi store hota hai
#         - apply_label() aur fetch_unread_emails() mein user_token pass hota hai
# ============================================================

import asyncio
import datetime
import json

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from sqlalchemy import select

from app.models.email import Email, EmailStatus
from app.models.thread import EmailThread, ThreadStatus
from app.models.user import User
from app.services.gmail_service import fetch_unread_emails, apply_label


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, name="app.workers.tasks.email_poller.fetch_new_emails_task")
def fetch_new_emails_task(self):
    """Fetch unread Gmail for ALL active users → save to DB → dispatch AI processor."""
    try:
        run_async(_fetch_and_save())
    except Exception as exc:
        print(f"[Poller] Task failed: {exc}")
        raise self.retry(exc=exc, countdown=30)


async def _fetch_and_save():
    async with AsyncSessionLocal() as db:

        # ── 1. Saare active users fetch karo ────────────────────
        users_result = await db.execute(
            select(User).where(User.is_active == True)
        )
        users = users_result.scalars().all()

        if not users:
            print("[Poller] No active users found — skipping poll")
            return

        print(f"[Poller] Polling emails for {len(users)} active user(s)")

        all_new_email_ids = []

        # ── 2. Har user ke liye alag alag emails fetch karo ─────
        for user in users:

            if not user.gmail_token:
                print(f"[Poller] User {user.email} has no Gmail token — skipping")
                continue

            # Token string → dict
            try:
                user_token = json.loads(user.gmail_token)
            except Exception as e:
                print(f"[Poller] Token parse failed for {user.email}: {e}")
                continue

            # ── 3. Gmail se unread emails fetch karo ────────────
            try:
                raw_emails = fetch_unread_emails(
                    max_results=20,
                    user_token=user_token,     # ← user ka apna token
                )
            except Exception as e:
                print(f"[Poller] Gmail fetch error for {user.email}: {e}")
                continue

            if not raw_emails:
                print(f"[Poller] No new emails for {user.email}")
                continue

            print(f"[Poller] Found {len(raw_emails)} email(s) for {user.email}")

            new_email_ids = []

            for raw in raw_emails:
                gmail_id  = raw.get("gmail_id", "")
                thread_id = raw.get("thread_id", "")

                # ── 4. Skip if already saved ─────────────────────
                existing = await db.execute(
                    select(Email).where(Email.gmail_message_id == gmail_id)
                )
                if existing.scalar_one_or_none():
                    continue

                # ── 5. Upsert EmailThread ─────────────────────────
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

                # ── 6. Save Email (with user_id) ──────────────────
                email = Email(
                    gmail_message_id = gmail_id,
                    thread_id        = thread_id,
                    sender           = raw.get("sender", ""),
                    subject          = raw.get("subject", ""),
                    body             = raw.get("body", ""),
                    received_at      = datetime.datetime.utcnow(),
                    status           = EmailStatus.new,
                    has_attachments  = raw.get("has_attachments", False),
                    attachment_names = raw.get("attachment_names", "[]"),
                    user_id          = user.id,    # ← NEW: kaun sa user
                )
                db.add(email)
                await db.flush()   # get email.id

                new_email_ids.append(email.id)

                # ── 7. Apply Gmail label ──────────────────────────
                try:
                    apply_label(
                        gmail_id,
                        label="AI-Processed",
                        user_token=user_token,     # ← user ka apna token
                    )
                except Exception as e:
                    print(f"[Poller] Label apply failed for {gmail_id}: {e}")

            await db.commit()
            all_new_email_ids.extend(new_email_ids)
            print(f"[Poller] ✓ Saved {len(new_email_ids)} email(s) for {user.email}")

    # ── 8. Dispatch AI pipeline for each new email ───────────
    from app.workers.tasks.ai_processor import process_email_ai
    for eid in all_new_email_ids:
        process_email_ai.delay(eid)
        print(f"[Poller] Dispatched AI pipeline for email_id={eid}")

    print(f"[Poller] ✓ Total new emails saved: {len(all_new_email_ids)}")