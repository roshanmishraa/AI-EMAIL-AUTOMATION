# Import all models here so SQLAlchemy's metadata knows about every table.
# This file MUST be imported before create_all() in main.py lifespan.

from app.models.email import Email, EmailCategory, EmailSentiment, EmailStatus
from app.models.reply import EmailReply, ReplySource
from app.models.escalation import Escalation, EscalationReason, EscalationStatus
from app.models.knowledge_base import KnowledgeBase, KBChunk
from app.models.settings import SystemSettings
from app.models.thread import EmailThread, ThreadStatus
from app.models.settings import SystemSettings

__all__ = [
    "Email", "EmailCategory", "EmailSentiment", "EmailStatus",
    "EmailReply", "ReplySource",
    "Escalation", "EscalationReason", "EscalationStatus",
    "KnowledgeBase", "KBChunk",
    "SystemSettings",
    "EmailThread", "ThreadStatus",
]
