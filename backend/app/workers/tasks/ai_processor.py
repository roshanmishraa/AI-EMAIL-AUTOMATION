"""
AI Processor Celery Task
========================
Full pipeline for a single email:

  1.  Fetch Email from DB
  2.  clean_email_body()
  3.  classify_email()          → category + confidence
  4.  detect_sentiment()        → sentiment + intent + vip_signal
  4.5 Early exit for SPAM       → skip RAG/LLM entirely
  5.  generate_reply()          → draft reply (with RAG)
  6.  check_escalation()        → escalation reason or None
  7.  Save EmailReply to DB
  8.  Update Email status in DB
  9.  Save Escalation record if needed
  10. Send Slack alert if escalated
  11. (Optional) Auto-send if auto_send_mode=True
"""

import asyncio
import datetime

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from sqlalchemy import select

from app.models.email import Email, EmailStatus, EmailCategory, EmailSentiment
from app.models.reply import EmailReply, ReplySource
from app.models.escalation import Escalation, EscalationReason
from app.models.thread import EmailThread

from app.services.ai.preprocessor import clean_email_body
from app.services.ai.classifier import classify_email
from app.services.ai.sentiment import detect_sentiment
from app.services.ai.reply_generator import generate_reply
from app.services.escalation_service import check_escalation, CONFIDENCE_THRESHOLD  # ← ADDED CONFIDENCE_THRESHOLD import
from app.services.notification_service import send_escalation_alert
from app.services.gmail_service import send_reply as gmail_send_reply


# ──────────────────────────────────────────
# HELPER: run async code from sync Celery task
# ──────────────────────────────────────────
def run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ──────────────────────────────────────────
# MAIN TASK
# ──────────────────────────────────────────
@celery_app.task(bind=True, max_retries=2, name="app.workers.tasks.ai_processor.process_email_ai")
def process_email_ai(self, email_id: int):
    """
    Full AI pipeline for one email.
    Called by:
      - email_poller after saving a new email
      - POST /emails/{id}/process (manual trigger from frontend)
    """
    try:
        run_async(_pipeline(email_id))
    except Exception as exc:
        print(f"[AIProcessor] Task failed for email {email_id}: {exc}")
        raise self.retry(exc=exc, countdown=15)


# ──────────────────────────────────────────
# ASYNC PIPELINE (all DB + AI calls are async)
# ──────────────────────────────────────────
async def _pipeline(email_id: int):
    async with AsyncSessionLocal() as db:

        # ── STEP 1: Fetch email ──────────────────────────
        email = await db.get(Email, email_id)
        if not email:
            print(f"[AIProcessor] Email {email_id} not found — skipping")
            return

        if email.status not in (EmailStatus.new, EmailStatus.processing):
            print(f"[AIProcessor] Email {email_id} already processed — skipping")
            return

        # Mark as processing so duplicate tasks don't double-process
        email.status = EmailStatus.processing
        await db.commit()

        # ── STEP 2: Clean body ──────────────────────────
        clean_body = clean_email_body(email.body or "", is_html=False)

        # ── STEP 3: Classify ────────────────────────────
        try:
            cls_result  = await classify_email(email.subject or "", clean_body)
            category    = cls_result.category
            cls_conf    = cls_result.confidence    # 0–100
        except Exception as e:
            print(f"[AIProcessor] Classifier failed: {e}")
            category  = "general"
            cls_conf  = 50.0

        # ── STEP 4: Sentiment + Intent ──────────────────
        try:
            sent_result = await detect_sentiment(clean_body)
            sentiment   = sent_result.sentiment
            intent      = sent_result.intent
            is_vip      = sent_result.is_vip_signal
        except Exception as e:
            print(f"[AIProcessor] Sentiment failed: {e}")
            sentiment = "neutral"
            intent    = "general"
            is_vip    = False

        # ── STEP 4.5: Early exit for SPAM ───────────────
        # Skip RAG + LLM entirely for spam/irrelevant emails
        # to avoid token waste and hallucinated replies
        SKIP_REPLY_CATEGORIES = {"spam"}

        if category in SKIP_REPLY_CATEGORIES:
            print(f"[AIProcessor] Email {email_id} is SPAM — skipping RAG/LLM entirely")

            # Save minimal reply placeholder (no LLM used)
            reply = EmailReply(
                email_id=email_id,
                generated_by=ReplySource.ai,
                reply_text="[SPAM — No reply generated. This email was identified as spam or irrelevant to BeastLife customer support.]",
                tone_used="none",
                confidence_score=cls_conf,
                is_approved=False,
                created_at=datetime.datetime.utcnow(),
            )
            db.add(reply)

            # Update email fields
            email.category         = category
            email.sentiment        = sentiment
            email.intent           = str(intent)
            email.confidence_score = cls_conf
            email.status           = EmailStatus.escalated

            await db.flush()

            # Save escalation record
            esc = Escalation(
                email_id=email_id,
                reason=EscalationReason.low_confidence,
                created_at=datetime.datetime.utcnow(),
            )
            db.add(esc)

            await db.commit()

            print(
                f"[AIProcessor] ✓ Email {email_id} | category=spam | "
                f"RAG skipped | LLM skipped | tokens saved ✅"
            )
            return  # ← Pipeline stops here for spam

        # ── STEP 5: Generate reply (RAG included) ───────
        try:
            reply_result = await generate_reply(
                subject=email.subject or "",
                body=clean_body,
                category=category,
                sentiment=sentiment,
            )
            draft_text      = reply_result.draft_reply
            reply_conf      = reply_result.confidence_score
            llm_esc_flag    = reply_result.escalation_flag
            tone_used       = reply_result.tone_used
        except Exception as e:
            print(f"[AIProcessor] ReplyGenerator failed: {e}")
            draft_text   = "Thank you for contacting us. Our team will review your message shortly."
            reply_conf   = 40.0
            llm_esc_flag = True
            tone_used    = "fallback"

        # Combine confidences (use lower of classifier + reply)
        final_conf = min(cls_conf, reply_conf)

        # ── STEP 6: Get thread message count for escalation check ──
        thread_count = 1
        if email.thread_id:
            thread_result = await db.execute(
                select(EmailThread).where(
                    EmailThread.gmail_thread_id == email.thread_id
                )
            )
            thread = thread_result.scalar_one_or_none()
            if thread:
                thread_count = thread.message_count or 1

        # VIP flag → escalation
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

        # ── FIX: LLM escalation flag sirf tab use karo jab confidence bhi low ho ──
        # BEFORE (buggy): if llm_esc_flag and escalation_reason is None:
        # AFTER  (fixed):  confidence check bhi lagaya → high-conf emails ab PROCESSED rahenge
        if llm_esc_flag and escalation_reason is None and final_conf < CONFIDENCE_THRESHOLD:
            escalation_reason = EscalationReason.low_confidence

        # ── STEP 7: Save EmailReply ─────────────────────
        reply = EmailReply(
            email_id=email_id,
            generated_by=ReplySource.ai,
            reply_text=draft_text,
            tone_used=tone_used,
            confidence_score=final_conf,
            is_approved=False,
            created_at=datetime.datetime.utcnow(),
        )
        db.add(reply)

        # ── STEP 8: Update Email fields ─────────────────
        email.category         = category
        email.sentiment        = sentiment
        email.intent           = str(intent)
        email.confidence_score = final_conf
        email.status           = (
            EmailStatus.escalated if escalation_reason
            else EmailStatus.processed
        )

        await db.flush()   # get reply.id before commit

        # ── STEP 9: Save Escalation record ─────────────
        if escalation_reason:
            esc = Escalation(
                email_id=email_id,
                reason=escalation_reason,
                created_at=datetime.datetime.utcnow(),
            )
            db.add(esc)

        await db.commit()

        # ── STEP 10: Slack alert ────────────────────────
        if escalation_reason:
            try:
                await send_escalation_alert(
                    email_id=email_id,
                    reason=str(escalation_reason),
                )
            except Exception as e:
                print(f"[AIProcessor] Slack alert failed (non-critical): {e}")

        # ── STEP 11: Auto-send if mode enabled ──────────
        try:
            from app.models.settings import SystemSettings
            settings_result = await db.execute(select(SystemSettings).limit(1))
            sys_settings    = settings_result.scalar_one_or_none()

            if sys_settings and sys_settings.auto_send_mode and not escalation_reason:
                sent = gmail_send_reply(
                    thread_id=email.thread_id or "",
                    to=email.sender or "",
                    subject=email.subject or "",
                    body=draft_text,
                )
                if sent:
                    reply.is_approved = True
                    reply.sent_at     = datetime.datetime.utcnow()
                    email.status      = EmailStatus.replied
                    await db.commit()
        except Exception as e:
            print(f"[AIProcessor] Auto-send failed (non-critical): {e}")

        print(
            f"[AIProcessor] ✓ Email {email_id} | category={category} | "
            f"sentiment={sentiment} | conf={final_conf:.1f} | "
            f"escalated={bool(escalation_reason)}"
        )