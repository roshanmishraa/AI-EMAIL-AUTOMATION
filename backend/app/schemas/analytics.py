from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_emails: int
    auto_replied: int
    escalated: int
    pending: int
    avg_confidence: float
    category_breakdown: dict
    sentiment_breakdown: dict
