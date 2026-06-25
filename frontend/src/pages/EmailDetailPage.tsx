import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Zap } from 'lucide-react'
import Topbar from '../components/layout/Topbar'
import Badge from '../components/common/Badge'
import AIReplyPanel from '../components/inbox/AIReplyPanel'
import ThreadView from '../components/inbox/ThreadView'
import { useEmail, useProcessEmail } from '../hooks/useEmails'
import { formatDateTime } from '../utils/date'

export default function EmailDetailPage() {
  const { id }         = useParams<{ id: string }>()
  const navigate       = useNavigate()
  const emailId        = Number(id)

  const { data: email, isLoading } = useEmail(emailId)
  const processEmail               = useProcessEmail()

  if (isLoading) {
    return (
      <div className="flex flex-col h-full">
        <Topbar title="Email" />
        <div className="flex-1 flex items-center justify-center text-gray-400">Loading…</div>
      </div>
    )
  }

  if (!email) {
    return (
      <div className="flex flex-col h-full">
        <Topbar title="Email not found" />
        <div className="flex-1 flex items-center justify-center text-gray-400">Email not found</div>
      </div>
    )
  }

  const latestReply = email.replies?.[email.replies.length - 1] ?? null

  return (
    <div className="flex flex-col h-full">
      <Topbar
        title={email.subject || '(No subject)'}
        subtitle={`From: ${email.sender}`}
        actions={
          <button
            onClick={() => navigate('/inbox')}
            className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800"
          >
            <ArrowLeft size={14} /> Back
          </button>
        }
      />

      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto p-6 space-y-6">

          {/* ── Email metadata badges ── */}
          <div className="flex flex-wrap items-center gap-2">
            <Badge label={email.status} variant="status" value={email.status} />
            {email.category && (
              <Badge label={email.category.replace('_', ' ')} variant="category" value={email.category} />
            )}
            {email.sentiment && (
              <Badge label={email.sentiment} variant="sentiment" value={email.sentiment} />
            )}
            {email.confidence_score != null && (
              <span className="text-xs text-gray-400 bg-gray-50 px-2 py-0.5 rounded-full border">
                {Math.round(email.confidence_score)}% confidence
              </span>
            )}
            <span className="text-xs text-gray-400 ml-auto">{formatDateTime(email.received_at)}</span>
          </div>

          {/* ── Email body ── */}
          <div className="bg-white border rounded-xl p-5">
            <div className="text-sm text-gray-500 mb-3 font-medium">Email Body</div>
            <div className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
              {email.body}
            </div>
          </div>

          {/* ── Thread history (if thread has more than 1 email) ── */}
          {email.thread_id && (
            <ThreadView threadId={email.thread_id} currentEmailId={emailId} />
          )}

          {/* ── AI Reply Panel or trigger button ── */}
          {email.status === 'new' || email.status === 'processing' ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-5 text-center">
              <p className="text-sm text-yellow-700 mb-3">
                {email.status === 'processing'
                  ? '⏳ AI pipeline is running… refresh in a moment.'
                  : 'This email has not been processed yet.'}
              </p>
              {email.status === 'new' && (
                <button
                  onClick={() => processEmail.mutate(emailId)}
                  disabled={processEmail.isPending}
                  className="flex items-center gap-2 mx-auto px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <Zap size={14} />
                  {processEmail.isPending ? 'Processing…' : 'Run AI Pipeline'}
                </button>
              )}
            </div>
          ) : (
            <AIReplyPanel email={email} reply={latestReply} />
          )}

        </div>
      </div>
    </div>
  )
}