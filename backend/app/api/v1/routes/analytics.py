from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

from app.core.deps import get_db, verify_api_key
from app.models.email import Email, EmailStatus, EmailCategory, EmailSentiment
from app.models.escalation import Escalation, EscalationReason      # ← NEW
from app.models.reply import EmailReply                              # ← NEW
from app.schemas.analytics import DashboardStats, SentimentTrendPoint  # ← NEW

router = APIRouter(dependencies=[Depends(verify_api_key)])


# -----------------------------
# DASHBOARD ANALYTICS
# -----------------------------
@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard(db: AsyncSession = Depends(get_db)):

    # -------------------------
    # TOTAL EMAILS
    # -------------------------
    total_result = await db.execute(select(func.count(Email.id)))
    total_emails = total_result.scalar() or 0

    # -------------------------
    # STATUS WISE COUNTS
    # -------------------------
    processed_result = await db.execute(
        select(func.count(Email.id)).where(Email.status == EmailStatus.processed)
    )
    processed = processed_result.scalar() or 0

    escalated_result = await db.execute(
        select(func.count(Email.id)).where(Email.status == EmailStatus.escalated)
    )
    escalated = escalated_result.scalar() or 0

    replied_result = await db.execute(
        select(func.count(Email.id)).where(Email.status == EmailStatus.replied)
    )
    replied = replied_result.scalar() or 0

    # -------------------------
    # CATEGORY DISTRIBUTION
    # -------------------------
    cat_result = await db.execute(
        select(Email.category, func.count(Email.id))
        .group_by(Email.category)
    )
    category_distribution = {
        str(k): v for k, v in cat_result.all() if k is not None
    }

    # -------------------------
    # SENTIMENT DISTRIBUTION
    # -------------------------
    sent_result = await db.execute(
        select(Email.sentiment, func.count(Email.id))
        .group_by(Email.sentiment)
    )
    sentiment_distribution = {
        str(k): v for k, v in sent_result.all() if k is not None
    }

    # -------------------------
    # AVERAGE CONFIDENCE SCORE
    # -------------------------
    conf_result = await db.execute(
        select(func.avg(Email.confidence_score))
    )
    avg_confidence = conf_result.scalar() or 0

    # ─────────────────────────────────────────
    # NEW: TOP ESCALATION REASONS
    # Escalation table mein reason column group karke count karo
    # e.g. {"legal": 4, "low_confidence": 3, "angry_repeat": 1}
    # ─────────────────────────────────────────
    esc_reason_result = await db.execute(
        select(Escalation.reason, func.count(Escalation.id))
        .group_by(Escalation.reason)
    )
    escalation_reasons = {
        str(k): v for k, v in esc_reason_result.all() if k is not None
    }

    # ─────────────────────────────────────────
    # NEW: AVERAGE RESPONSE TIME (seconds)
    # EmailReply.created_at - Email.received_at = kitni der mein AI ne reply banaya
    # Sirf woh emails jahan reply exist karta hai aur received_at bhi set hai
    # ─────────────────────────────────────────
    avg_response_time_seconds = None
    try:
        rt_result = await db.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        EmailReply.created_at - Email.received_at
                    )
                )
            )
            .join(Email, EmailReply.email_id == Email.id)
            .where(Email.received_at.isnot(None))
        )
        rt_val = rt_result.scalar()
        if rt_val is not None:
            avg_response_time_seconds = round(float(rt_val), 2)
    except Exception as e:
        # Non-critical — agar DB mein received_at column nahi hai toh gracefully skip
        print(f"[Analytics] avg_response_time query failed (non-critical): {e}")
        avg_response_time_seconds = None

    # ─────────────────────────────────────────
    # NEW: SENTIMENT TREND — last 7 days
    # Har din ka sentiment breakdown — ek list of {date, sentiment_counts}
    # ─────────────────────────────────────────
    sentiment_trend: list[SentimentTrendPoint] = []
    try:
        today = datetime.date.today()

        for i in range(6, -1, -1):                          # day-6 → day-0 (oldest → newest)
            day = today - datetime.timedelta(days=i)
            day_start = datetime.datetime.combine(day, datetime.time.min)
            day_end   = datetime.datetime.combine(day, datetime.time.max)

            day_sent_result = await db.execute(
                select(Email.sentiment, func.count(Email.id))
                .where(Email.received_at >= day_start)
                .where(Email.received_at <= day_end)
                .where(Email.sentiment.isnot(None))
                .group_by(Email.sentiment)
            )

            sentiment_counts = {
                str(k): v for k, v in day_sent_result.all() if k is not None
            }

            sentiment_trend.append(
                SentimentTrendPoint(
                    date=day.strftime("%Y-%m-%d"),
                    sentiment_counts=sentiment_counts,  # {} if no emails that day — frontend handles it
                )
            )
    except Exception as e:
        print(f"[Analytics] sentiment_trend query failed (non-critical): {e}")
        sentiment_trend = []

    # -------------------------
    # RESPONSE
    # -------------------------
    return {
        "total_emails":              total_emails,
        "processed":                 processed,
        "escalated":                 escalated,
        "replied":                   replied,
        "category_distribution":     category_distribution,
        "sentiment_distribution":    sentiment_distribution,
        "avg_confidence":            round(float(avg_confidence), 2),

        # ── NEW fields ──
        "escalation_reasons":        escalation_reasons,
        "avg_response_time_seconds": avg_response_time_seconds,
        "sentiment_trend":           sentiment_trend,
    }