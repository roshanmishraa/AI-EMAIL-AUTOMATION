from typing import Optional

from app.models.escalation import EscalationReason
from app.models.email import EmailCategory, EmailSentiment


# -----------------------------
# CONFIG
# -----------------------------
CONFIDENCE_THRESHOLD = 70.0

LEGAL_KEYWORDS = [
    "lawsuit", "legal action", "attorney", "lawyer", "gdpr",
    "sue", "court", "compliance", "breach", "violation"
]

SENSITIVE_ATTACHMENT_KEYWORDS = [
    "attached", "attachment", "enclosed", "document", "medical",
    "prescription", "legal document", "contract", "certificate"
]


# -----------------------------
# ESCALATION ENGINE
# -----------------------------
def check_escalation(
    category: str,
    sentiment: str,
    confidence: float,
    body: str,
    thread_message_count: int = 1,
) -> Optional[EscalationReason]:
    """
    Escalation decision engine based on AI outputs.
    Returns EscalationReason or None.
    """

    body_lower = (body or "").lower()

    # -----------------------------
    # RULE 1: LEGAL (HIGHEST PRIORITY)
    # -----------------------------
    if category == "legal":
        return EscalationReason.legal

    if any(kw in body_lower for kw in LEGAL_KEYWORDS):
        return EscalationReason.legal

    # -----------------------------
    # RULE 1b: SENSITIVE ATTACHMENT
    # -----------------------------
    if any(kw in body_lower for kw in SENSITIVE_ATTACHMENT_KEYWORDS):
        if category in ("legal", "billing"):
            return EscalationReason.sensitive_attachment

    # -----------------------------
    # RULE 2: ANGRY + REPEAT ISSUE
    # -----------------------------
    if sentiment == "angry" and thread_message_count >= 3:
        return EscalationReason.angry_repeat

    # -----------------------------
    # RULE 3: LOW CONFIDENCE MODEL
    # -----------------------------
    if confidence < CONFIDENCE_THRESHOLD:
        return EscalationReason.low_confidence

    # -----------------------------
    # NO ESCALATION
    # -----------------------------
    return None