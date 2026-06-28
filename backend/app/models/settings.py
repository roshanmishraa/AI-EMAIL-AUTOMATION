# ============================================================
# FILE:  backend/app/models/settings.py
# CHANGE: agent_email aur email_notify_on_escalation fields add kiye
# ============================================================

from sqlalchemy import Column, Integer, Boolean, String, Time
from app.db.base import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True)

    # ── Existing fields (UNCHANGED) ──────────────────────────
    auto_send_mode                   = Column(Boolean, default=False)
    escalation_confidence_threshold  = Column(Integer, default=70)
    polling_interval_seconds         = Column(Integer, default=60)

    # ── SLA Targets (UNCHANGED) ──────────────────────────────
    sla_response_time_minutes        = Column(Integer, default=60)
    sla_escalation_time_minutes      = Column(Integer, default=30)

    # ── Working Hours (UNCHANGED) ─────────────────────────────
    working_hours_start              = Column(String, default="09:00")
    working_hours_end                = Column(String, default="18:00")
    working_days                     = Column(String, default="Mon,Tue,Wed,Thu,Fri")

    # ── Slack Notifications (UNCHANGED) ──────────────────────
    slack_notify_on_escalation       = Column(Boolean, default=True)
    slack_notify_on_legal            = Column(Boolean, default=True)

    # ── NEW: Email ping settings ──────────────────────────────
    # Email address of the support agent/team to ping on escalation
    agent_email                      = Column(String, default="", nullable=True)

    # Toggle to enable/disable email pings (separate from Slack)
    email_notify_on_escalation       = Column(Boolean, default=True)