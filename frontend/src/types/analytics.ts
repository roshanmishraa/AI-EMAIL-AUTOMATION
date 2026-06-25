export interface DashboardStats {
  total_emails: number
  processed: number
  replied: number
  escalated: number
  avg_confidence: number
  category_distribution: Record<string, number>
  sentiment_distribution: Record<string, number>
}