import { Email } from '../types/email'
import { formatDateTime } from '../types/date'
import Badge from '../common/Badge'

interface ThreadViewProps {
  emails: Email[]           // all messages in the thread, oldest first
  currentEmailId: number   // highlight the selected one
}

export default function ThreadView({ emails, currentEmailId }: ThreadViewProps) {
  if (emails.length <= 1) return null   // no thread to show if only one message

  return (
    <div className="border rounded-xl bg-white overflow-hidden">
      <div className="px-4 py-3 border-b bg-gray-50">
        <span className="text-sm font-medium text-gray-700">
          Thread history · {emails.length} messages
        </span>
      </div>

      <div className="divide-y divide-gray-50">
        {emails.map((email, idx) => {
          const isCurrent = email.id === currentEmailId
          return (
            <div
              key={email.id}
              className={`px-4 py-3 ${isCurrent ? 'bg-blue-50 border-l-2 border-l-blue-500' : 'hover:bg-gray-50'}`}
            >
              <div className="flex items-start justify-between gap-3 mb-1.5">
                <div className="flex items-center gap-2 min-w-0">
                  <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-medium text-xs shrink-0">
                    {email.sender?.[0]?.toUpperCase() ?? '?'}
                  </div>
                  <span className="text-sm font-medium text-gray-800 truncate">
                    {email.sender}
                  </span>
                  {isCurrent && (
                    <span className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded font-medium shrink-0">
                      Current
                    </span>
                  )}
                </div>
                <span className="text-xs text-gray-400 shrink-0">
                  {formatDateTime(email.received_at)}
                </span>
              </div>

              <p className="text-xs text-gray-600 ml-8 line-clamp-2 leading-relaxed">
                {email.body?.slice(0, 200)}
                {(email.body?.length ?? 0) > 200 ? '…' : ''}
              </p>

              {(email.status || email.sentiment || email.category) && (
                <div className="flex gap-1.5 mt-2 ml-8 flex-wrap">
                  {email.status && (
                    <Badge label={email.status} variant="status" value={email.status} />
                  )}
                  {email.sentiment && (
                    <Badge label={email.sentiment} variant="sentiment" value={email.sentiment} />
                  )}
                  {email.category && (
                    <Badge
                      label={email.category.replace('_', ' ')}
                      variant="category"
                      value={email.category}
                    />
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}