from pydantic import BaseModel
from typing import Dict


class DashboardStats(BaseModel):
    # These names MUST match the keys returned by analytics.py route exactly
    total_emails: int
    processed: int        # emails with status=processed
    replied: int          # emails with status=replied
    escalated: int        # emails with status=escalated
    avg_confidence: float
    category_distribution: Dict[str, int]   # e.g. {"billing": 5, "legal": 2}
    sentiment_distribution: Dict[str, int]  # e.g. {"angry": 3, "neutral": 10}