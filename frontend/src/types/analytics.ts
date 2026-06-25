export interface DashboardStats {
  // These EXACTLY match what GET /api/v1/analytics/dashboard returns
  total_emails:            number
  processed:               number   // status=processed count
  replied:                 number   // status=replied count
  escalated:               number   // status=escalated count
  avg_confidence:          number   // 0–100
  category_distribution:   Record<string, number>  // {"billing": 5, "legal": 2, ...}
  sentiment_distribution:  Record<string, number>  // {"angry": 3, "neutral": 10, ...}
}