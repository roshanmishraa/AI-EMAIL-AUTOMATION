from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
import datetime

# -----------------------------
# ENUMS (KEEP THESE - GOOD DESIGN)
# -----------------------------

class EmailCategory(str, enum.Enum):
    legal = "legal"
    billing = "billing"
    product_issue = "product_issue"
    delivery = "delivery"
    refund = "refund"
    general = "general"
    spam = "spam"
    feedback = "feedback"


class EmailSentiment(str, enum.Enum):
    angry = "angry"
    frustrated = "frustrated"
    neutral = "neutral"
    happy = "happy"
    sad = "sad"


class EmailStatus(str, enum.Enum):
    new = "new"
    processing = "processing"
    processed = "processed"
    replied = "replied"
    escalated = "escalated"


# -----------------------------
# EMAIL TABLE
# -----------------------------

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    gmail_message_id = Column(String, unique=True, index=True)
    thread_id = Column(String, index=True)

    sender = Column(String)
    subject = Column(String)
    body = Column(Text)

    received_at = Column(DateTime, default=datetime.datetime.utcnow)

    # -----------------------------
    # AI GENERATED FIELDS
    # -----------------------------
    category = Column(Enum(EmailCategory), nullable=True)
    sentiment = Column(Enum(EmailSentiment), nullable=True)

    # IMPORTANT: replaced JSONB with TEXT for SQLite compatibility
    intent = Column(Text, nullable=True)

    confidence_score = Column(Float, nullable=True)
    status = Column(Enum(EmailStatus), default=EmailStatus.new)

    # -----------------------------
    # RELATIONSHIPS
    # -----------------------------
    replies = relationship("EmailReply", back_populates="email")
    escalations = relationship("Escalation", back_populates="email")
