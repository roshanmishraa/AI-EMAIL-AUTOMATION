from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, verify_api_key
from app.models.email import Email, EmailStatus, EmailCategory, EmailSentiment
from app.schemas.analytics import DashboardStats

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

    # -------------------------
    # RESPONSE
    # -------------------------
    return {
        "total_emails": total_emails,
        "processed": processed,
        "escalated": escalated,
        "replied": replied,
        "category_distribution": category_distribution,
        "sentiment_distribution": sentiment_distribution,
        "avg_confidence": round(float(avg_confidence), 2)
    }