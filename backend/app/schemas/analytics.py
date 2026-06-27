from pydantic import BaseModel
from typing import Dict, List


# ── Sentiment trend ka ek data point (1 din = 1 object) ──
class SentimentTrendPoint(BaseModel):
    date: str                          # "2026-06-27"
    sentiment_counts: Dict[str, int]   # {"angry": 2, "neutral": 5, "happy": 1}


class DashboardStats(BaseModel):
    # These names MUST match the keys returned by analytics.py route exactly

    # ── Existing fields (unchanged) ──
    total_emails: int
    processed: int                          # emails with status=processed
    replied: int                            # emails with status=replied
    escalated: int                          # emails with status=escalated
    avg_confidence: float
    category_distribution: Dict[str, int]   # e.g. {"billing": 5, "legal": 2}
    sentiment_distribution: Dict[str, int]  # e.g. {"angry": 3, "neutral": 10}

    # ── NEW: Top escalation reasons ──
    # e.g. {"legal": 4, "low_confidence": 3, "angry_repeat": 1}
    escalation_reasons: Dict[str, int]

    # ── NEW: Avg response time in seconds (AI auto-reply kitni der mein hua) ──
    # None agar abhi tak koi reply send nahi hua
    avg_response_time_seconds: float | None

    # ── NEW: Sentiment trend — last 7 days, ek point per day ──
    sentiment_trend: List[SentimentTrendPoint]