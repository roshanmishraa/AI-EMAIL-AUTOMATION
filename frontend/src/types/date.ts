/**
 * Format a date string as a human-readable relative time.
 * e.g. "2 hours ago", "just now", "3 days ago"
 *
 * FIX: Backend returns UTC datetime without 'Z' suffix (e.g. "2026-06-27T13:05:00")
 * Browser treats this as LOCAL time → wrong diff
 * Solution: append 'Z' if no timezone info present → forces UTC parsing
 */
export function formatDistanceToNow(dateStr: string): string {
  if (!dateStr) return ''

  // FIX: append 'Z' to treat as UTC if no timezone offset present
  const normalized = /[Zz]|[+-]\d{2}:\d{2}$/.test(dateStr) ? dateStr : dateStr + 'Z'
  const date = new Date(normalized)
  if (isNaN(date.getTime())) return dateStr

  const now       = Date.now()
  const diffMs    = now - date.getTime()
  const diffSecs  = Math.floor(diffMs / 1000)
  const diffMins  = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays  = Math.floor(diffHours / 24)

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
 *
 * FIX: Same UTC normalization as above
 */
export function formatDateTime(dateStr: string): string {
  if (!dateStr) return ''

  // FIX: append 'Z' to treat as UTC if no timezone offset present
  const normalized = /[Zz]|[+-]\d{2}:\d{2}$/.test(dateStr) ? dateStr : dateStr + 'Z'
  const date = new Date(normalized)
  if (isNaN(date.getTime())) return dateStr

  return date.toLocaleString('en-GB', {
    day:    'numeric',
    month:  'short',
    year:   'numeric',
    hour:   '2-digit',
    minute: '2-digit',
  })
}