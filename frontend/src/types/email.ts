export type EmailStatus = 'new' | 'processing' | 'processed' | 'replied' | 'escalated'

export type EmailCategory =
  | 'legal'
  | 'billing'
  | 'product_issue'
  | 'delivery'
  | 'refund'
  | 'general'
  | 'spam'
  | 'feedback'

export type EmailSentiment = 'angry' | 'frustrated' | 'neutral' | 'happy' | 'sad'

// NEW: escalation reason/status types — backend ke Enum se match karte hain
export type EscalationReason =
  | 'legal'
  | 'vip'
  | 'low_confidence'
  | 'angry_repeat'
  | 'sensitive_attachment'
  | 'manual_review'

export type EscalationStatusType = 'open' | 'in_progress' | 'resolved'

export interface Escalation {
  id: number
  reason: EscalationReason
  status: EscalationStatusType
  notes: string | null
  created_at: string | null
  resolved_at: string | null
}

export interface EmailReply {
  id: number
  email_id: number
  generated_by: 'ai' | 'human'
  reply_text: string
  tone_used: string | null
  confidence_score: number | null
  is_approved: boolean
  sent_at: string | null
  created_at: string
}

export interface Email {
  id: number
  gmail_message_id: string
  thread_id: string | null
  sender: string
  subject: string
  body: string
  received_at: string
  category: EmailCategory | null
  sentiment: EmailSentiment | null
  intent: string | null
  confidence_score: number | null
  status: EmailStatus
  has_attachments: boolean        // NEW: pehle missing tha
  attachment_names: string | null // NEW: pehle missing tha (JSON string)
  replies: EmailReply[]
  escalations: Escalation[]       // NEW
}

export interface EmailListOut {
  emails: Email[]
  total: number
}

/**
 * Returns the latest AI-generated (not human) draft reply for an email,
 * or null if none exist. Used by AIReplyPanel.
 */
export function getLatestAIDraft(email: Email): EmailReply | null {
  if (!email.replies || email.replies.length === 0) return null

  // Filter to AI-generated drafts, newest first (highest id)
  const aiReplies = email.replies
    .filter(r => r.generated_by === 'ai')
    .sort((a, b) => b.id - a.id)

  return aiReplies[0] ?? null
}

/**
 * NEW: Returns the latest (open or in_progress) escalation for an email,
 * or null if none/all resolved. Used by AIReplyPanel to show the reason
 * and the Resolve button.
 */
export function getLatestEscalation(email: Email): Escalation | null {
  if (!email.escalations || email.escalations.length === 0) return null

  const sorted = [...email.escalations].sort((a, b) => b.id - a.id)
  return sorted[0] ?? null
}