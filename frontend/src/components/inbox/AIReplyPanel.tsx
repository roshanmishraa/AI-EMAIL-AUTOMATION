import { useState, useEffect } from 'react'
import { CheckCircle, AlertTriangle, Cpu, Edit3, RotateCcw, Send } from 'lucide-react'
import LoadingSpinner from '../common/LoadingSpinner'
import { Email, EmailReply, getLatestAIDraft, getLatestEscalation } from '../../types/email'
import { useApproveReply, useEscalateEmail, useProcessEmail, useResolveEscalation } from '../../hooks/useEmails'

interface AIReplyPanelProps {
  email: Email
}

// reason codes → human-readable labels
const REASON_LABELS: Record<string, string> = {
  legal:                 'Legal — needs legal/compliance review',
  vip:                   'VIP customer',
  low_confidence:        'Low AI confidence',
  angry_repeat:          'Angry customer — repeated contact',
  sensitive_attachment:  'Sensitive attachment detected',
  manual_review:         'Manually escalated by agent',
}

export default function AIReplyPanel({ email }: AIReplyPanelProps) {
  const draft: EmailReply | null = getLatestAIDraft(email)
  const escalation = getLatestEscalation(email)

  const [editedText, setEditedText]   = useState(draft?.reply_text ?? '')
  const [isEditing,  setIsEditing]    = useState(false)
  const [resolveNotes, setResolveNotes] = useState('')

  // Keep textarea in sync if draft arrives after initial render
  useEffect(() => {
    if (draft?.reply_text && !isEditing) {
      setEditedText(draft.reply_text)
    }
  }, [draft?.reply_text])

  const approve  = useApproveReply()
  const escalate = useEscalateEmail()
  const process  = useProcessEmail()
  const resolve  = useResolveEscalation()

  const confidence = draft?.confidence_score ?? null
  const isApproved = draft?.is_approved ?? false
  const alreadyEsc = email.status === 'escalated'
  const alreadyRep = email.status === 'replied'
  const isResolved = escalation?.status === 'resolved'

  // Confidence colour
  const confColor =
    confidence == null ? 'bg-gray-200'   :
    confidence >= 80   ? 'bg-green-500'  :
    confidence >= 60   ? 'bg-yellow-400' :
                         'bg-red-500'

  // ── No draft yet ─────────────────────────────────────────
  if (!draft) {
    const isProcessing = email.status === 'processing'
    return (
      <div className="border rounded-xl bg-white p-6 flex flex-col items-center justify-center gap-4 min-h-[200px]">
        {isProcessing ? (
          <>
            <LoadingSpinner size="lg" />
            <p className="text-sm text-gray-500">AI is generating a reply…</p>
          </>
        ) : (
          <>
            <Cpu size={32} className="text-gray-300" />
            <p className="text-sm text-gray-500 text-center">No AI draft yet.</p>
            <button
              onClick={() => process.mutate(email.id)}
              disabled={process.isPending}
              className="flex items-center gap-2 text-sm bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white px-4 py-2 rounded-lg transition-colors"
            >
              {process.isPending ? <LoadingSpinner size="sm" /> : <Cpu size={14} />}
              {process.isPending ? 'Running pipeline…' : 'Run AI Pipeline'}
            </button>
          </>
        )}
      </div>
    )
  }

  // ── Already replied / approved ────────────────────────────
  if (isApproved || alreadyRep) {
    return (
      <div className="border rounded-xl bg-green-50 border-green-200 p-5">
        <div className="flex items-center gap-2 text-green-700 font-medium mb-3">
          <CheckCircle size={16} />
          Reply sent
          {draft.sent_at && (
            <span className="text-xs font-normal text-green-600 ml-1">
              · {new Date(draft.sent_at).toLocaleString()}
            </span>
          )}
        </div>
        <p className="text-sm text-green-800 whitespace-pre-wrap leading-relaxed">
          {draft.reply_text}
        </p>
      </div>
    )
  }

  // ── ESCALATED VIEW ────────────────────────────────────────
  // FIX: "Approve & Send" button add kiya taaki human review ke
  // baad reply bhi bhej sake, sirf resolve na kare
  if (alreadyEsc) {
    return (
      <div className="border rounded-xl bg-red-50 border-red-200 overflow-hidden">

        {/* Header */}
        <div className="px-5 pt-5 pb-3">
          <div className="flex items-center gap-2 text-red-700 font-medium mb-3">
            <AlertTriangle size={16} />
            Escalated for human review
          </div>

          {/* Reason badge */}
          {escalation && !isResolved && (
            <div className="mb-3 inline-flex items-center gap-1.5 text-xs font-medium text-red-700 bg-red-100 border border-red-200 px-2.5 py-1 rounded-full">
              Reason: {REASON_LABELS[escalation.reason] ?? escalation.reason}
            </div>
          )}

          {/* Resolved badge */}
          {isResolved && (
            <div className="mb-3 inline-flex items-center gap-1.5 text-xs font-medium text-green-700 bg-green-100 border border-green-200 px-2.5 py-1 rounded-full">
              <CheckCircle size={12} /> Resolved
              {escalation?.resolved_at && (
                <span className="font-normal">
                  · {new Date(escalation.resolved_at).toLocaleString()}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Draft text — editable even in escalated state */}
        <div className="px-5 pb-4">
          <p className="text-xs text-gray-500 mb-1.5 font-medium">AI Draft Reply:</p>
          {isEditing ? (
            <textarea
              value={editedText}
              onChange={e => setEditedText(e.target.value)}
              rows={8}
              className="w-full text-sm text-gray-700 border border-red-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-red-400 resize-none leading-relaxed bg-white"
              autoFocus
            />
          ) : (
            <p className="text-sm text-red-800 whitespace-pre-wrap leading-relaxed bg-red-50 rounded-lg">
              {editedText}
            </p>
          )}
        </div>

        {/* Actions — sirf jab resolved nahi hua */}
        {!isResolved && (
          <div className="border-t border-red-200 px-5 py-4 space-y-3 bg-white">

            {/* Edit toggle */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsEditing(v => !v)}
                className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 bg-white hover:bg-gray-50 px-3 py-1.5 rounded-lg transition-colors"
              >
                {isEditing
                  ? <><RotateCcw size={13} /> Cancel Edit</>
                  : <><Edit3 size={13} /> Edit Draft</>
                }
              </button>
              <span className="text-xs text-gray-400">
                Edit the draft before sending
              </span>
            </div>

            {/* ── FIX: Approve & Send button ── */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => approve.mutate(email.id)}
                disabled={approve.isPending}
                className="flex items-center gap-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60 px-4 py-2 rounded-lg transition-colors font-medium"
              >
                {approve.isPending ? <LoadingSpinner size="sm" /> : <Send size={13} />}
                {approve.isPending ? 'Sending…' : 'Approve & Send Reply'}
              </button>
              <span className="text-xs text-gray-400">
                Sends reply via Gmail
              </span>
            </div>

            {approve.isError && (
              <p className="text-xs text-red-600">Send failed — check backend connection.</p>
            )}

            {/* Divider */}
            <div className="border-t border-red-100 pt-3">
              <p className="text-xs text-gray-400 mb-2">
                Or mark as resolved without sending a reply:
              </p>
              <div className="space-y-2">
                <input
                  type="text"
                  value={resolveNotes}
                  onChange={e => setResolveNotes(e.target.value)}
                  placeholder="Review notes (optional)…"
                  className="w-full text-sm border border-red-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-red-300 bg-white"
                />
                <button
                  onClick={() => resolve.mutate({ id: email.id, notes: resolveNotes || undefined })}
                  disabled={resolve.isPending}
                  className="flex items-center gap-1.5 text-sm text-white bg-red-600 hover:bg-red-700 disabled:opacity-60 px-4 py-1.5 rounded-lg transition-colors font-medium"
                >
                  {resolve.isPending ? <LoadingSpinner size="sm" /> : <CheckCircle size={13} />}
                  {resolve.isPending ? 'Resolving…' : 'Mark Resolved (no reply)'}
                </button>
                {resolve.isError && (
                  <p className="text-xs text-red-600">Failed to resolve — try again.</p>
                )}
              </div>
            </div>

          </div>
        )}
      </div>
    )
  }

  // ── Normal draft (not escalated, not replied) ─────────────
  return (
    <div className="border rounded-xl bg-white overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-gray-50">
        <div className="flex items-center gap-2">
          <Cpu size={15} className="text-blue-600" />
          <span className="text-sm font-medium text-gray-800">AI Draft</span>
          {draft.tone_used && (
            <span className="text-xs text-gray-400 capitalize">· {draft.tone_used} tone</span>
          )}
        </div>

        {/* Confidence bar */}
        {confidence != null && (
          <div className="flex items-center gap-2">
            <div className="w-24 h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${confColor}`}
                style={{ width: `${confidence}%` }}
              />
            </div>
            <span className={`text-xs font-medium ${
              confidence >= 80 ? 'text-green-600' :
              confidence >= 60 ? 'text-yellow-600' :
              'text-red-600'
            }`}>
              {Math.round(confidence)}%
            </span>
          </div>
        )}
      </div>

      {/* Reply text / editor */}
      <div className="p-4">
        {isEditing ? (
          <textarea
            value={editedText}
            onChange={e => setEditedText(e.target.value)}
            rows={8}
            className="w-full text-sm text-gray-700 border border-blue-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none leading-relaxed"
            autoFocus
          />
        ) : (
          <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed min-h-[80px]">
            {editedText}
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50 gap-2 flex-wrap">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsEditing(v => !v)}
            className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 bg-white hover:bg-gray-50 px-3 py-1.5 rounded-lg transition-colors"
          >
            {isEditing ? <><RotateCcw size={13} /> Cancel</> : <><Edit3 size={13} /> Edit</>}
          </button>

          <button
            onClick={() => escalate.mutate(email.id)}
            disabled={escalate.isPending}
            className="flex items-center gap-1.5 text-sm text-red-600 hover:text-red-700 border border-red-200 bg-red-50 hover:bg-red-100 disabled:opacity-60 px-3 py-1.5 rounded-lg transition-colors"
          >
            {escalate.isPending ? <LoadingSpinner size="sm" /> : <AlertTriangle size={13} />}
            Escalate
          </button>
        </div>

        <button
          onClick={() => approve.mutate(email.id)}
          disabled={approve.isPending}
          className="flex items-center gap-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60 px-4 py-1.5 rounded-lg transition-colors font-medium"
        >
          {approve.isPending ? <LoadingSpinner size="sm" /> : <CheckCircle size={13} />}
          {approve.isPending ? 'Sending…' : 'Approve & Send'}
        </button>
      </div>

      {/* Error feedback */}
      {(approve.isError || escalate.isError) && (
        <div className="px-4 pb-3 text-xs text-red-600">
          Action failed — check backend connection.
        </div>
      )}
    </div>
  )
}
