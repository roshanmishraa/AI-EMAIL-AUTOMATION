from sqlalchemy import Column, Integer, Boolean, String, Time
from app.db.base import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True)

    # ── Existing fields (unchanged) ──
    auto_send_mode                   = Column(Boolean, default=False)
    escalation_confidence_threshold  = Column(Integer, default=70)
    polling_interval_seconds         = Column(Integer, default=60)

    # ── NEW: SLA Targets (minutes) ──
    sla_response_time_minutes        = Column(Integer, default=60)    # AI reply SLA
    sla_escalation_time_minutes      = Column(Integer, default=30)    # Escalation acknowledge SLA

    # ── NEW: Working Hours ──
    # Store as "HH:MM" string — simple, timezone-free, easy to render in frontend
    working_hours_start              = Column(String, default="09:00")  # e.g. "09:00"
    working_hours_end                = Column(String, default="18:00")  # e.g. "18:00"
    working_days                     = Column(String, default="Mon,Tue,Wed,Thu,Fri")  # comma-separated

    # ── NEW: Notification preferences ──
    slack_notify_on_escalation       = Column(Boolean, default=True)
    slack_notify_on_legal            = Column(Boolean, default=True)