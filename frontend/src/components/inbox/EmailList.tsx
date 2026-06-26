import { Link } from 'react-router-dom'
import { Email } from '../../types/email'
import Badge from '../common/Badge'
import { formatDistanceToNow } from '../../types/date'

interface EmailListProps {
  emails: Email[]
  loading?: boolean
}

export default function EmailList({ emails, loading }: EmailListProps) {
  if (loading) {
    return (
      <div className="divide-y divide-gray-100">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="px-6 py-4 flex gap-4 animate-pulse">
            <div className="w-8 h-8 bg-gray-200 rounded-full shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4" />
              <div className="h-3 bg-gray-100 rounded w-1/2" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (!emails.length) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="text-4xl mb-3">📭</div>
        <div className="text-gray-500 font-medium">No emails found</div>
        <div className="text-gray-400 text-sm mt-1">Try changing your filters or trigger a Gmail fetch</div>
      </div>
    )
  }

  return (
    <div className="divide-y divide-gray-100">
      {emails.map(email => (
        <Link
          key={email.id}
          to={`/inbox/${email.id}`}
          className="flex items-start gap-4 px-6 py-4 hover:bg-gray-50 transition-colors group"
        >
          {/* Avatar */}
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-medium text-sm shrink-0 mt-0.5">
            {email.sender?.[0]?.toUpperCase() ?? '?'}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2 mb-1">
              <div className="flex items-center gap-2 min-w-0">
                <span className="text-sm font-medium text-gray-900 truncate">{email.sender}</span>
                {email.status === 'escalated' && (
                  <span className="text-xs text-red-600 font-semibold shrink-0">🚨 Escalated</span>
                )}
              </div>
              <span className="text-xs text-gray-400 shrink-0">
                {formatDistanceToNow(email.received_at)}
              </span>
            </div>

            <div className="text-sm text-gray-800 font-medium truncate mb-1.5">
              {email.subject}
            </div>

            <div className="text-xs text-gray-500 truncate mb-2">
              {email.body?.slice(0, 120)}...
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <Badge label={email.status} variant="status" value={email.status} />
              {email.category && (
                <Badge
                  label={email.category.replace('_', ' ')}
                  variant="category"
                  value={email.category}
                />
              )}
              {email.sentiment && (
                <Badge label={email.sentiment} variant="sentiment" value={email.sentiment} />
              )}
              {email.confidence_score != null && (
                <span className="text-xs text-gray-400">
                  {Math.round(email.confidence_score)}% confidence
                </span>
              )}
            </div>
          </div>
        </Link>
      ))}
    </div>
  )
}
