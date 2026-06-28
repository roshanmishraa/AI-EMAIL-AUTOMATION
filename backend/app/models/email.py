# ============================================================
# FILE:  backend/app/models/email.py
# CHANGE: has_attachments aur attachment_names columns add kiye
# ============================================================

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Enum,
    ForeignKey,
    Boolean,      # ← NEW
)

from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
import datetime


# -----------------------------
# ENUMS (UNCHANGED)
# -----------------------------

class EmailCategory(str, enum.Enum):
    legal         = "legal"
    billing       = "billing"
    product_issue = "product_issue"
    delivery      = "delivery"
    refund        = "refund"
    general       = "general"
    spam          = "spam"
    feedback      = "feedback"


class EmailSentiment(str, enum.Enum):
    angry     = "angry"
    frustrated = "frustrated"
    neutral   = "neutral"
    happy     = "happy"
    sad       = "sad"


class EmailStatus(str, enum.Enum):
    new        = "new"
    processing = "processing"
    processed  = "processed"
    replied    = "replied"
    escalated  = "escalated"


# -----------------------------
# EMAIL TABLE
# -----------------------------

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    gmail_message_id = Column(String, unique=True, index=True)
    thread_id        = Column(String, index=True)

    sender  = Column(String)
    subject = Column(String)
    body    = Column(Text)

    received_at = Column(DateTime, default=datetime.datetime.utcnow)

    # ── AI generated fields (UNCHANGED) ──────────────────────
    category         = Column(Enum(EmailCategory), nullable=True)
    sentiment        = Column(Enum(EmailSentiment), nullable=True)
    intent           = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    status           = Column(Enum(EmailStatus), default=EmailStatus.new)

    # ── NEW: Attachment fields ────────────────────────────────
    # has_attachments: quick boolean for filtering/display
    # attachment_names: JSON list stored as Text, e.g. '["invoice.pdf","photo.jpg"]'
    has_attachments  = Column(Boolean, default=False, nullable=False)
    attachment_names = Column(Text, default="[]", nullable=True)

    # ── Relationships (UNCHANGED) ─────────────────────────────
    replies     = relationship("EmailReply", back_populates="email")
    escalations = relationship("Escalation", back_populates="email")
