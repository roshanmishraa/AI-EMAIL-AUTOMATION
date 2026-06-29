"""
AI Processor Celery Task — SYNC VERSION
========================================
asyncpg Windows pe Celery ke saath event loop crash karta hai.
Fix: psycopg2 sync engine use karo (SyncSessionLocal).
Async functions (classify, sentiment, generate_reply) ke liye
asyncio.run() use karo — yeh har call pe fresh event loop banata hai.
"""

import asyncio
import datetime
import json

from app.workers.celery_app import celery_app
from app.db.session import SyncSessionLocal
from sqlalchemy import select

from app.models.email import Email, EmailStatus
from app.models.reply import EmailReply, ReplySource
from app.models.escalation import Escalation, EscalationReason
from app.models.thread import EmailThread
from app.models.user import User

from app.services.ai.preprocessor import clean_email_body
from app.services.ai.classifier import classify_email
from app.services.ai.sentiment import detect_sentiment
from app.services.ai.reply_generator import generate_reply
from app.services.escalation_service import check_escalation
from app.services.notification_service import send_escalation_alert
from app.services.gmail_service import send_reply as gmail_send_reply


def run_async(coro):
    """Fresh event loop har async call ke liye — Windows safe."""
    return asyncio.run(coro)


@celery_app.task(bind=True, max_retries=2, name="app.workers.tasks.ai_processor.process_email_ai")
def process_email_ai(self, email_id: int):
    try:
        _pipeline(email_id)
    except Exception as exc:
        print(f"[AIProcessor] Task failed for email {email_id}: {exc}")
        raise self.retry(exc=exc, countdown=15)


def _pipeline(email_id: int):
    with SyncSessionLocal() as db:

        # ── STEP 1: Fetch email ──────────────────────────────
        email = db.get(Email, email_id)
        if not email:
            print(f"[AIProcessor] Email {email_id} not found — skipping")
            return

        if email.status not in (EmailStatus.new, EmailStatus.processing):
            print(f"[AIProcessor] Email {email_id} already processed — skipping")
            return

        email.status = EmailStatus.processing
        db.commit()

        # ── STEP 2: Clean body ───────────────────────────────
        # FIX: Auto-detect HTML emails instead of hardcoded is_html=False
        raw_body = email.body or ""
        is_html = any(tag in raw_body.lower() for tag in [
            "<html", "<!doctype", "<head>", "<body", "<table", "<div", "<span", "<style"
        ])
        clean_body = clean_email_body(raw_body, is_html=is_html)

        # ── STEP 3: Classify ─────────────────────────────────
        # NOTE: classifier ko raw_body bhejna better hai HTML detection ke liye
        # clean_body mein HTML tags already strip ho chuke hote hain
        try:
            cls_result = run_async(classify_email(email.subject or "", raw_body))
            category   = cls_result.category
            cls_conf   = cls_result.confidence
        except Exception as e:
            print(f"[AIProcessor] Classifier failed: {e}")
            category = "general"
            cls_conf = 50.0

        # ── STEP 4: Sentiment ────────────────────────────────
        # Sentiment ke liye clean_body use karo (HTML stripped)
        try:
            sent_result = run_async(detect_sentiment(clean_body))
            sentiment   = sent_result.sentiment
            intent      = sent_result.intent
            is_vip      = sent_result.is_vip_signal
        except Exception as e:
            print(f"[AIProcessor] Sentiment failed: {e}")
            sentiment = "neutral"
            intent    = "general"
            is_vip    = False

        # ── STEP 4.5: SPAM early exit ─────────────────────────
        if category == "spam":
            print(f"[AIProcessor] Email {email_id} is SPAM — skipping RAG/LLM")

            reply = EmailReply(
                email_id         = email_id,
                generated_by     = ReplySource.ai,
                reply_text       = "[SPAM — No reply generated.]",
                tone_used        = "none",
                confidence_score = cls_conf,
                is_approved      = False,
                created_at       = datetime.datetime.utcnow(),
            )
            db.add(reply)

            email.category         = category
            email.sentiment        = sentiment
            email.intent           = str(intent)
            email.confidence_score = cls_conf
            email.status           = EmailStatus.processed
            db.commit()

            print(f"[AIProcessor] ✓ Email {email_id} | spam | tokens saved ✅")
            return

        # ── STEP 5: Generate reply (RAG) ─────────────────────
        try:
            reply_result = run_async(generate_reply(
                subject=email.subject or "",
                body=clean_body,      # RAG ke liye clean body
                category=category,
                sentiment=sentiment,
            ))
            draft_text   = reply_result.draft_reply
            reply_conf   = reply_result.confidence_score
            llm_esc_flag = reply_result.escalation_flag
            tone_used    = reply_result.tone_used
        except Exception as e:
            print(f"[AIProcessor] ReplyGenerator failed: {e}")
            draft_text   = "Thank you for contacting us. Our team will review your message shortly."
            reply_conf   = 40.0
            llm_esc_flag = True
            tone_used    = "fallback"

        final_conf = min(cls_conf, reply_conf)

        # ── STEP 6: Thread count for escalation ──────────────
        thread_count = 1
        if email.thread_id:
            thread = db.execute(
                select(EmailThread).where(
                    EmailThread.gmail_thread_id == email.thread_id
                )
            ).scalar_one_or_none()
            if thread:
                thread_count = thread.message_count or 1

        # ── STEP 6.5: Escalation check ───────────────────────
        escalation_reason = None
        if is_vip:
            escalation_reason = EscalationReason.vip
        else:
            escalation_reason = check_escalation(
                category=category,
                sentiment=sentiment,
                confidence=final_conf,
                body=clean_body,
                thread_message_count=thread_count,
            )

        # ── STEP 7: Save reply ───────────────────────────────
        reply = EmailReply(
            email_id         = email_id,
            generated_by     = ReplySource.ai,
            reply_text       = draft_text,
            tone_used        = tone_used,
            confidence_score = final_conf,
            is_approved      = False,
            created_at       = datetime.datetime.utcnow(),
        )
        db.add(reply)

        # ── STEP 8: Update email ─────────────────────────────
        email.category         = category
        email.sentiment        = sentiment
        email.intent           = str(intent)
        email.confidence_score = final_conf
        email.status           = (
            EmailStatus.escalated if escalation_reason
            else EmailStatus.processed
        )
        db.flush()

        # ── STEP 9: Save escalation ──────────────────────────
        if escalation_reason:
            esc = Escalation(
                email_id   = email_id,
                reason     = escalation_reason,
                created_at = datetime.datetime.utcnow(),
            )
            db.add(esc)

        # ── STEP 10: Slack alert ─────────────────────────────
        if escalation_reason:
            try:
                run_async(send_escalation_alert(
                    email_id=email_id,
                    reason=str(escalation_reason),
                ))
            except Exception as e:
                print(f"[AIProcessor] Slack alert failed: {e}")

        # ── STEP 11: Auto-send ───────────────────────────────
        auto_sent = False
        try:
            from app.models.settings import SystemSettings
            sys_settings = db.execute(
                select(SystemSettings).limit(1)
            ).scalar_one_or_none()

            if sys_settings and sys_settings.auto_send_mode and not escalation_reason:
                user_token = None
                if email.user_id:
                    owner = db.get(User, email.user_id)
                    if owner and owner.gmail_token:
                        user_token = json.loads(owner.gmail_token)

                sent = gmail_send_reply(
                    thread_id=email.thread_id or "",
                    to=email.sender or "",
                    subject=email.subject or "",
                    body=draft_text,
                    user_token=user_token,
                )

                if sent:
                    reply.is_approved = True
                    reply.sent_at     = datetime.datetime.utcnow()
                    email.status      = EmailStatus.replied
                    auto_sent         = True
                    print(f"[AIProcessor] ✅ Auto-sent reply for email {email_id}")
        except Exception as e:
            print(f"[AIProcessor] Auto-send failed: {e}")

        # ── FINAL COMMIT ─────────────────────────────────────
        db.commit()

        print(
            f"[AIProcessor] ✓ Email {email_id} | category={category} | "
            f"sentiment={sentiment} | conf={final_conf:.1f} | "
            f"escalated={bool(escalation_reason)} | auto_sent={auto_sent}"
        )