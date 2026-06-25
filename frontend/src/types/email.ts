export interface Email {
  id: number
  gmail_message_id: string
  sender: string
  subject: string
  body: string
  received_at: string
  category: string | null
  sentiment: string | null
  intent: object | null
  confidence_score: number | null
  status: 'new' | 'processing' | 'processed' | 'replied' | 'escalated'
}
