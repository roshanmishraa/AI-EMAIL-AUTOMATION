# ============================================================
# FILE:  backend/app/api/v1/routes/notifications.py
# NEW FILE — create karo is path pe
# Endpoint: GET /notifications/unread-count
#           Returns count of open escalations
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.deps import get_db, verify_api_key
from app.models.escalation import Escalation, EscalationStatus

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/unread-count")
async def get_unread_count(db: AsyncSession = Depends(get_db)):
    """
    Returns the count of open (unresolved) escalations.
    Frontend sidebar badge calls this every 30 seconds.
    """
    result = await db.execute(
        select(func.count(Escalation.id)).where(
            Escalation.status == EscalationStatus.open
        )
    )
    count = result.scalar() or 0

    return {
        "unread_count": count,
        "has_unread":   count > 0,
    }