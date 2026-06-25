from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, verify_api_key
from app.models.settings import SystemSettings

router = APIRouter(dependencies=[Depends(verify_api_key)])


# -------------------------
# GET SETTINGS
# -------------------------
@router.get("/")
async def get_settings(db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(SystemSettings).limit(1))
    settings = result.scalar_one_or_none()

    if not settings:
        settings = SystemSettings()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return {
        "auto_send_mode": settings.auto_send_mode,
        "escalation_confidence_threshold": settings.escalation_confidence_threshold,
        "polling_interval_seconds": settings.polling_interval_seconds,
    }


# -------------------------
# UPDATE SETTINGS
# -------------------------
@router.post("/")
async def update_settings(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(SystemSettings).limit(1))
    settings = result.scalar_one_or_none()

    if not settings:
        settings = SystemSettings()
        db.add(settings)

    if "auto_send_mode" in payload:
        settings.auto_send_mode = payload["auto_send_mode"]

    if "escalation_confidence_threshold" in payload:
        settings.escalation_confidence_threshold = payload["escalation_confidence_threshold"]

    if "polling_interval_seconds" in payload:
        settings.polling_interval_seconds = payload["polling_interval_seconds"]

    await db.commit()

    return {
        "updated": True,
        "settings": {
            "auto_send_mode": settings.auto_send_mode,
            "escalation_confidence_threshold": settings.escalation_confidence_threshold,
            "polling_interval_seconds": settings.polling_interval_seconds,
        }
    }
