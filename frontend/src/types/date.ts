/**
 * Format a date string as a human-readable relative time.
 * e.g. "2 hours ago", "just now", "3 days ago"
 */
export function formatDistanceToNow(dateStr: string): string {
  if (!dateStr) return ''

  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr

  const now        = Date.now()
  const diffMs     = now - date.getTime()
  const diffSecs   = Math.floor(diffMs / 1000)
  const diffMins   = Math.floor(diffSecs / 60)
  const diffHours  = Math.floor(diffMins / 60)
  const diffDays   = Math.floor(diffHours / 24)

  if (diffSecs < 60)  return 'just now'
  if (diffMins < 60)  return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7)   return `${diffDays}d ago`

  return date.toLocaleDateString('en-GB', {
    day:   'numeric',
    month: 'short',
    year:  diffDays > 365 ? 'numeric' : undefined,
  })
}

/**
 * Format a date string as a full human readable timestamp.
 * e.g. "25 Jun 2026, 14:30"
 */
export function formatDateTime(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr

  return date.toLocaleString('en-GB', {
    day:    'numeric',
    month:  'short',
    year:   'numeric',
    hour:   '2-digit',
    minute: '2-digit',
  })
}