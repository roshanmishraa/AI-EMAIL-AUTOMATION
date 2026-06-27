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
        # ── Existing fields (unchanged) ──
        "auto_send_mode":                  settings.auto_send_mode,
        "escalation_confidence_threshold": settings.escalation_confidence_threshold,
        "polling_interval_seconds":        settings.polling_interval_seconds,

        # ── NEW: SLA targets ──
        "sla_response_time_minutes":       settings.sla_response_time_minutes,
        "sla_escalation_time_minutes":     settings.sla_escalation_time_minutes,

        # ── NEW: Working hours ──
        "working_hours_start":             settings.working_hours_start,
        "working_hours_end":               settings.working_hours_end,
        "working_days":                    settings.working_days,

        # ── NEW: Notification preferences ──
        "slack_notify_on_escalation":      settings.slack_notify_on_escalation,
        "slack_notify_on_legal":           settings.slack_notify_on_legal,
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

    # ── Existing fields (unchanged) ──
    if "auto_send_mode" in payload:
        settings.auto_send_mode = payload["auto_send_mode"]

    if "escalation_confidence_threshold" in payload:
        settings.escalation_confidence_threshold = payload["escalation_confidence_threshold"]

    if "polling_interval_seconds" in payload:
        settings.polling_interval_seconds = payload["polling_interval_seconds"]

    # ── NEW: SLA targets ──
    if "sla_response_time_minutes" in payload:
        settings.sla_response_time_minutes = int(payload["sla_response_time_minutes"])

    if "sla_escalation_time_minutes" in payload:
        settings.sla_escalation_time_minutes = int(payload["sla_escalation_time_minutes"])

    # ── NEW: Working hours ──
    if "working_hours_start" in payload:
        settings.working_hours_start = payload["working_hours_start"]

    if "working_hours_end" in payload:
        settings.working_hours_end = payload["working_hours_end"]

    if "working_days" in payload:
        settings.working_days = payload["working_days"]

    # ── NEW: Notification preferences ──
    if "slack_notify_on_escalation" in payload:
        settings.slack_notify_on_escalation = payload["slack_notify_on_escalation"]

    if "slack_notify_on_legal" in payload:
        settings.slack_notify_on_legal = payload["slack_notify_on_legal"]

    await db.commit()

    return {
        "updated": True,
        "settings": {
            # ── Existing ──
            "auto_send_mode":                  settings.auto_send_mode,
            "escalation_confidence_threshold": settings.escalation_confidence_threshold,
            "polling_interval_seconds":        settings.polling_interval_seconds,

            # ── NEW ──
            "sla_response_time_minutes":       settings.sla_response_time_minutes,
            "sla_escalation_time_minutes":     settings.sla_escalation_time_minutes,
            "working_hours_start":             settings.working_hours_start,
            "working_hours_end":               settings.working_hours_end,
            "working_days":                    settings.working_days,
            "slack_notify_on_escalation":      settings.slack_notify_on_escalation,
            "slack_notify_on_legal":           settings.slack_notify_on_legal,
        }
    }
