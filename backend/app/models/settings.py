from sqlalchemy import Column, Integer, Boolean
from app.db.base import Base


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True)

    auto_send_mode = Column(Boolean, default=False)
    escalation_confidence_threshold = Column(Integer, default=70)
    polling_interval_seconds = Column(Integer, default=60)