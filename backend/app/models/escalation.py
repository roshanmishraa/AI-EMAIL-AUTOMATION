from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class EscalationReason(str, enum.Enum):
    legal           = "legal"
    vip             = "vip"
    low_confidence  = "low_confidence"
    angry_repeat    = "angry_repeat"
    sensitive_attachment = "sensitive_attachment"


class EscalationStatus(str, enum.Enum):
    open        = "open"
    in_progress = "in_progress"
    resolved    = "resolved"


class Escalation(Base):
    __tablename__ = "escalations"

    id          = Column(Integer, primary_key=True, index=True)
    email_id    = Column(Integer, ForeignKey("emails.id"))
    reason      = Column(Enum(EscalationReason))
    status      = Column(Enum(EscalationStatus), default=EscalationStatus.open)
    notes       = Column(String, nullable=True)
    created_at  = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    email       = relationship("Email", back_populates="escalations")
