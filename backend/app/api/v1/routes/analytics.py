from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

from app.core.deps import get_db, verify_api_key
from app.models.email import Email, EmailStatus
from app.models.escalation import Escalation
from app.models.reply import EmailReply
from app.schemas.analytics import DashboardStats, SentimentTrendPoint

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(
    user_id: int = Query(..., description="Logged-in user ka ID — sirf unka data aaye"),
    db: AsyncSession = Depends(get_db),
):

    # ── TOTAL EMAILS ──────────────────────────────────────
    total_result = await db.execute(
        select(func.count(Email.id)).where(Email.user_id == user_id)
    )
    total_emails = total_result.scalar() or 0

    # ── STATUS COUNTS ─────────────────────────────────────
    processed_result = await db.execute(
        select(func.count(Email.id))
        .where(Email.status == EmailStatus.processed)
        .where(Email.user_id == user_id)
    )
    processed = processed_result.scalar() or 0

    escalated_result = await db.execute(
        select(func.count(Email.id))
        .where(Email.status == EmailStatus.escalated)
        .where(Email.user_id == user_id)
    )
    escalated = escalated_result.scalar() or 0

    replied_result = await db.execute(
        select(func.count(Email.id))
        .where(Email.status == EmailStatus.replied)
        .where(Email.user_id == user_id)
    )
    replied = replied_result.scalar() or 0

    # ── CATEGORY DISTRIBUTION ─────────────────────────────
    cat_result = await db.execute(
        select(Email.category, func.count(Email.id))
        .where(Email.user_id == user_id)
        .group_by(Email.category)
    )
    category_distribution = {
        # FIX: .value extracts "general" not "EmailCategory.general"
        (k.value if hasattr(k, 'value') else str(k)): v
        for k, v in cat_result.all() if k is not None
    }

    # ── SENTIMENT DISTRIBUTION ────────────────────────────
    sent_result = await db.execute(
        select(Email.sentiment, func.count(Email.id))
        .where(Email.user_id == user_id)
        .group_by(Email.sentiment)
    )
    sentiment_distribution = {
        # FIX: .value extracts "angry" not "EmailSentiment.angry"
        (k.value if hasattr(k, 'value') else str(k)): v
        for k, v in sent_result.all() if k is not None
    }

    # ── AVG CONFIDENCE ────────────────────────────────────
    conf_result = await db.execute(
        select(func.avg(Email.confidence_score)).where(Email.user_id == user_id)
    )
    avg_confidence = conf_result.scalar() or 0

    # ── TOP ESCALATION REASONS ────────────────────────────
    # FIX: .value gives "low_confidence" not "EscalationReason.low_confidence"
    # NEW: Escalation table mein user_id nahi hai, isliye Email se join karke filter karo
    esc_reason_result = await db.execute(
        select(Escalation.reason, func.count(Escalation.id))
        .join(Email, Escalation.email_id == Email.id)
        .where(Email.user_id == user_id)
        .group_by(Escalation.reason)
    )
    escalation_reasons = {
        (k.value if hasattr(k, 'value') else str(k)): v
        for k, v in esc_reason_result.all() if k is not None
    }

    # ── AVG RESPONSE TIME (seconds) ───────────────────────
    # FIX: SQLite doesn't support func.extract("epoch", interval)
    # So we fetch all (reply.created_at, email.received_at) pairs and compute in Python
    avg_response_time_seconds = None
    try:
        rt_result = await db.execute(
            select(EmailReply.created_at, Email.received_at)
            .join(Email, EmailReply.email_id == Email.id)
            .where(Email.received_at.isnot(None))
            .where(EmailReply.created_at.isnot(None))
            .where(Email.user_id == user_id)
        )
        rows = rt_result.all()
        if rows:
            diffs = []
            for reply_created, email_received in rows:
                if reply_created and email_received:
                    diff = (reply_created - email_received).total_seconds()
                    # Sanity check: ignore negative/zero diffs (data issues)
                    if 0 < diff < 86400:   # between 0s and 24h
                        diffs.append(diff)
            if diffs:
                avg_response_time_seconds = round(sum(diffs) / len(diffs), 2)
    except Exception as e:
        print(f"[Analytics] avg_response_time query failed (non-critical): {e}")
        avg_response_time_seconds = None

    # ── SENTIMENT TREND — last 7 days ─────────────────────
    sentiment_trend: list[SentimentTrendPoint] = []
    try:
        today = datetime.date.today()
        for i in range(6, -1, -1):
            day       = today - datetime.timedelta(days=i)
            day_start = datetime.datetime.combine(day, datetime.time.min)
            day_end   = datetime.datetime.combine(day, datetime.time.max)

            day_sent_result = await db.execute(
                select(Email.sentiment, func.count(Email.id))
                .where(Email.received_at >= day_start)
                .where(Email.received_at <= day_end)
                .where(Email.sentiment.isnot(None))
                .where(Email.user_id == user_id)
                .group_by(Email.sentiment)
            )
            # FIX: .value here too
            sentiment_counts = {
                (k.value if hasattr(k, 'value') else str(k)): v
                for k, v in day_sent_result.all() if k is not None
            }
            sentiment_trend.append(
                SentimentTrendPoint(
                    date=day.strftime("%Y-%m-%d"),
                    sentiment_counts=sentiment_counts,
                )
            )
    except Exception as e:
        print(f"[Analytics] sentiment_trend query failed (non-critical): {e}")
        sentiment_trend = []

    return {
        "total_emails":              total_emails,
        "processed":                 processed,
        "escalated":                 escalated,
        "replied":                   replied,
        "category_distribution":     category_distribution,
        "sentiment_distribution":    sentiment_distribution,
        "avg_confidence":            round(float(avg_confidence), 2),
        "escalation_reasons":        escalation_reasons,
        "avg_response_time_seconds": avg_response_time_seconds,
        "sentiment_trend":           sentiment_trend,
    }