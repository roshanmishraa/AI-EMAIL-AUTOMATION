import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, ExternalLink } from 'lucide-react'
import { useEmail } from '../hooks/useEmails'
import Topbar from '../components/layout/Topbar'
import AIReplyPanel from '../components/inbox/AIReplyPanel'
import ThreadView from '../components/inbox/ThreadView'
import Badge from '../components/common/Badge'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { formatDateTime } from '../types/date'
import { useQuery } from '@tanstack/react-query'
import client from '../api/axiosClient'

export default function EmailDetailPage() {
  const { id }    = useParams<{ id: string }>()
  const navigate  = useNavigate()
  const emailId   = Number(id)

  const { data: email, isLoading, isError } = useEmail(emailId)

  // Fetch thread messages (if thread_id exists)
  const { data: threadData } = useQuery({
    queryKey: ['thread', email?.thread_id],
    queryFn:  () => client.get(`/emails/thread/${email!.thread_id}`).then(r => r.data),
    enabled:  !!email?.thread_id,
    select:   d => d.emails ?? [],
  })

  const threadEmails = threadData ?? (email ? [email] : [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (isError || !email) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3">
        <p className="text-gray-500">Email not found.</p>
        <button onClick={() => navigate('/inbox')} className="text-blue-600 text-sm hover:underline">
          ← Back to Inbox
        </button>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <Topbar
        title={email.subject || '(no subject)'}
        subtitle={`From: ${email.sender}`}
        actions={
          <button
            onClick={() => navigate('/inbox')}
            className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 bg-white px-3 py-1.5 rounded-lg"
          >
            <ArrowLeft size={14} /> Back
          </button>
        }
      />

      <div className="flex-1 overflow-auto p-6 grid grid-cols-3 gap-6 items-start">

        {/* LEFT — email body + thread + AI panel (2/3) */}
        <div className="col-span-2 flex flex-col gap-5">

          {/* Email body */}
          <div className="border rounded-xl bg-white overflow-hidden">
            <div className="px-5 py-4 border-b bg-gray-50 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-800">{email.sender}</p>
                <p className="text-xs text-gray-400 mt-0.5">{formatDateTime(email.received_at)}</p>
              </div>
              <a
                href={`https://mail.google.com/mail/u/0/#inbox/${email.gmail_message_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-gray-400 hover:text-blue-600 flex items-center gap-1"
              >
                Open in Gmail <ExternalLink size={11} />
              </a>
            </div>
            <div className="px-5 py-4">
              <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                {email.body}
              </p>
            </div>
          </div>

          {/* Thread history */}
          {threadEmails.length > 1 && (
            <ThreadView emails={threadEmails} currentEmailId={emailId} />
          )}

          {/* AI Reply Panel */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">AI Generated Reply</h3>
            <AIReplyPanel email={email} />
          </div>
        </div>

        {/* RIGHT — metadata sidebar (1/3) */}
        <div className="flex flex-col gap-4">

          {/* Status card */}
          <div className="border rounded-xl bg-white p-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Status</p>
            <div className="flex flex-col gap-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">Status</span>
                <Badge label={email.status} variant="status" value={email.status} />
              </div>
              {email.category && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Category</span>
                  <Badge
                    label={email.category.replace('_', ' ')}
                    variant="category"
                    value={email.category}
                  />
                </div>
              )}
              {email.sentiment && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">Sentiment</span>
                  <Badge label={email.sentiment} variant="sentiment" value={email.sentiment} />
                </div>
              )}
              {email.confidence_score != null && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">AI Confidence</span>
                  <span className={`text-xs font-medium ${
                    email.confidence_score >= 80 ? 'text-green-600' :
                    email.confidence_score >= 60 ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {Math.round(email.confidence_score)}%
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Details card */}
          <div className="border rounded-xl bg-white p-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Details</p>
            <div className="flex flex-col gap-2.5">
              <div>
                <p className="text-xs text-gray-400">Received</p>
                <p className="text-xs text-gray-700 mt-0.5">{formatDateTime(email.received_at)}</p>
              </div>
              {email.intent && (
                <div>
                  <p className="text-xs text-gray-400">Intent</p>
                  <p className="text-xs text-gray-700 mt-0.5 capitalize">
                    {email.intent.replace(/_/g, ' ')}
                  </p>
                </div>
              )}
              {email.thread_id && (
                <div>
                  <p className="text-xs text-gray-400">Thread ID</p>
                  <p className="text-xs text-gray-500 mt-0.5 font-mono truncate">
                    {email.thread_id}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Replies count */}
          {email.replies?.length > 0 && (
            <div className="border rounded-xl bg-white p-4">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                AI Drafts ({email.replies.length})
              </p>
              {email.replies.map((r, i) => (
                <div key={r.id} className="text-xs text-gray-500 py-1 border-b last:border-0 flex justify-between">
                  <span>Draft {i + 1} · {r.generated_by}</span>
                  <span className={r.is_approved ? 'text-green-600' : 'text-gray-400'}>
                    {r.is_approved ? '✓ Sent' : 'Pending'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}