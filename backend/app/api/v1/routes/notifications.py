# ============================================================
# FILE:  backend/app/api/v1/routes/notifications.py
# NEW FILE — create karo is path pe
# Endpoint: GET /notifications/unread-count
#           Returns count of open escalations
# ============================================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.deps import get_db, verify_api_key
from app.models.escalation import Escalation, EscalationStatus
from app.models.email import Email

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/unread-count")
async def get_unread_count(
    user_id: int = Query(..., description="Logged-in user ka ID — sirf unki escalations count ho"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the count of open (unresolved) escalations — sirf
    logged-in user ke emails ke liye (Escalation -> Email join).
    Frontend sidebar badge calls this every 30 seconds.
    """
    result = await db.execute(
        select(func.count(Escalation.id))
        .join(Email, Escalation.email_id == Email.id)
        .where(Escalation.status == EscalationStatus.open)
        .where(Email.user_id == user_id)
    )
    count = result.scalar() or 0

    return {
        "unread_count": count,
        "has_unread":   count > 0,
    }