// ── Sentiment trend ka ek data point (1 din = 1 object) ──
export interface SentimentTrendPoint {
  date: string                           // "2026-06-27"
  sentiment_counts: Record<string, number>  // {"angry": 2, "neutral": 5, "happy": 1}
}

export interface DashboardStats {
  // These EXACTLY match what GET /api/v1/analytics/dashboard returns

  // ── Existing fields (unchanged) ──
  total_emails:            number
  processed:               number   // status=processed count
  replied:                 number   // status=replied count
  escalated:               number   // status=escalated count
  avg_confidence:          number   // 0–100
  category_distribution:   Record<string, number>  // {"billing": 5, "legal": 2}
  sentiment_distribution:  Record<string, number>  // {"angry": 3, "neutral": 10}

  // ── NEW: Top escalation reasons ──
  // {"legal": 4, "low_confidence": 3, "angry_repeat": 1}
  escalation_reasons:          Record<string, number>

  // ── NEW: Avg AI response time in seconds (null if no replies yet) ──
  avg_response_time_seconds:   number | null

  // ── NEW: Sentiment trend — last 7 days ──
  sentiment_trend:             SentimentTrendPoint[]
}