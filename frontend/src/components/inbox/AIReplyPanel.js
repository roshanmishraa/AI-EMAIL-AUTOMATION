import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from 'react';
import { CheckCircle, AlertTriangle, Cpu, Edit3, RotateCcw, Send } from 'lucide-react';
import LoadingSpinner from '../common/LoadingSpinner';
import { getLatestAIDraft, getLatestEscalation } from '../../types/email';
import { useApproveReply, useEscalateEmail, useProcessEmail, useResolveEscalation } from '../../hooks/useEmails';
// reason codes → human-readable labels
const REASON_LABELS = {
    legal: 'Legal — needs legal/compliance review',
    vip: 'VIP customer',
    low_confidence: 'Low AI confidence',
    angry_repeat: 'Angry customer — repeated contact',
    sensitive_attachment: 'Sensitive attachment detected',
    manual_review: 'Manually escalated by agent',
};
export default function AIReplyPanel({ email }) {
    const draft = getLatestAIDraft(email);
    const escalation = getLatestEscalation(email);
    const [editedText, setEditedText] = useState(draft?.reply_text ?? '');
    const [isEditing, setIsEditing] = useState(false);
    const [resolveNotes, setResolveNotes] = useState('');
    // Keep textarea in sync if draft arrives after initial render
    useEffect(() => {
        if (draft?.reply_text && !isEditing) {
            setEditedText(draft.reply_text);
        }
    }, [draft?.reply_text]);
    const approve = useApproveReply();
    const escalate = useEscalateEmail();
    const process = useProcessEmail();
    const resolve = useResolveEscalation();
    const confidence = draft?.confidence_score ?? null;
    const isApproved = draft?.is_approved ?? false;
    const alreadyEsc = email.status === 'escalated';
    const alreadyRep = email.status === 'replied';
    const isResolved = escalation?.status === 'resolved';
    // Confidence colour
    const confColor = confidence == null ? 'bg-gray-200' :
        confidence >= 80 ? 'bg-green-500' :
            confidence >= 60 ? 'bg-yellow-400' :
                'bg-red-500';
    // ── No draft yet ─────────────────────────────────────────
    if (!draft) {
        const isProcessing = email.status === 'processing';
        return (_jsx("div", { className: "border rounded-xl bg-white p-6 flex flex-col items-center justify-center gap-4 min-h-[200px]", children: isProcessing ? (_jsxs(_Fragment, { children: [_jsx(LoadingSpinner, { size: "lg" }), _jsx("p", { className: "text-sm text-gray-500", children: "AI is generating a reply\u2026" })] })) : (_jsxs(_Fragment, { children: [_jsx(Cpu, { size: 32, className: "text-gray-300" }), _jsx("p", { className: "text-sm text-gray-500 text-center", children: "No AI draft yet." }), _jsxs("button", { onClick: () => process.mutate(email.id), disabled: process.isPending, className: "flex items-center gap-2 text-sm bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white px-4 py-2 rounded-lg transition-colors", children: [process.isPending ? _jsx(LoadingSpinner, { size: "sm" }) : _jsx(Cpu, { size: 14 }), process.isPending ? 'Running pipeline…' : 'Run AI Pipeline'] })] })) }));
    }
    // ── Already replied / approved ────────────────────────────
    if (isApproved || alreadyRep) {
        return (_jsxs("div", { className: "border rounded-xl bg-green-50 border-green-200 p-5", children: [_jsxs("div", { className: "flex items-center gap-2 text-green-700 font-medium mb-3", children: [_jsx(CheckCircle, { size: 16 }), "Reply sent", draft.sent_at && (_jsxs("span", { className: "text-xs font-normal text-green-600 ml-1", children: ["\u00B7 ", new Date(draft.sent_at).toLocaleString()] }))] }), _jsx("p", { className: "text-sm text-green-800 whitespace-pre-wrap leading-relaxed", children: draft.reply_text })] }));
    }
    // ── ESCALATED VIEW ────────────────────────────────────────
    // FIX: "Approve & Send" button add kiya taaki human review ke
    // baad reply bhi bhej sake, sirf resolve na kare
    if (alreadyEsc) {
        return (_jsxs("div", { className: "border rounded-xl bg-red-50 border-red-200 overflow-hidden", children: [_jsxs("div", { className: "px-5 pt-5 pb-3", children: [_jsxs("div", { className: "flex items-center gap-2 text-red-700 font-medium mb-3", children: [_jsx(AlertTriangle, { size: 16 }), "Escalated for human review"] }), escalation && !isResolved && (_jsxs("div", { className: "mb-3 inline-flex items-center gap-1.5 text-xs font-medium text-red-700 bg-red-100 border border-red-200 px-2.5 py-1 rounded-full", children: ["Reason: ", REASON_LABELS[escalation.reason] ?? escalation.reason] })), isResolved && (_jsxs("div", { className: "mb-3 inline-flex items-center gap-1.5 text-xs font-medium text-green-700 bg-green-100 border border-green-200 px-2.5 py-1 rounded-full", children: [_jsx(CheckCircle, { size: 12 }), " Resolved", escalation?.resolved_at && (_jsxs("span", { className: "font-normal", children: ["\u00B7 ", new Date(escalation.resolved_at).toLocaleString()] }))] }))] }), _jsxs("div", { className: "px-5 pb-4", children: [_jsx("p", { className: "text-xs text-gray-500 mb-1.5 font-medium", children: "AI Draft Reply:" }), isEditing ? (_jsx("textarea", { value: editedText, onChange: e => setEditedText(e.target.value), rows: 8, className: "w-full text-sm text-gray-700 border border-red-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-red-400 resize-none leading-relaxed bg-white", autoFocus: true })) : (_jsx("p", { className: "text-sm text-red-800 whitespace-pre-wrap leading-relaxed bg-red-50 rounded-lg", children: editedText }))] }), !isResolved && (_jsxs("div", { className: "border-t border-red-200 px-5 py-4 space-y-3 bg-white", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("button", { onClick: () => setIsEditing(v => !v), className: "flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 bg-white hover:bg-gray-50 px-3 py-1.5 rounded-lg transition-colors", children: isEditing
                                        ? _jsxs(_Fragment, { children: [_jsx(RotateCcw, { size: 13 }), " Cancel Edit"] })
                                        : _jsxs(_Fragment, { children: [_jsx(Edit3, { size: 13 }), " Edit Draft"] }) }), _jsx("span", { className: "text-xs text-gray-400", children: "Edit the draft before sending" })] }), _jsxs("div", { className: "flex items-center gap-2", children: [_jsxs("button", { onClick: () => approve.mutate(email.id), disabled: approve.isPending, className: "flex items-center gap-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60 px-4 py-2 rounded-lg transition-colors font-medium", children: [approve.isPending ? _jsx(LoadingSpinner, { size: "sm" }) : _jsx(Send, { size: 13 }), approve.isPending ? 'Sending…' : 'Approve & Send Reply'] }), _jsx("span", { className: "text-xs text-gray-400", children: "Sends reply via Gmail" })] }), approve.isError && (_jsx("p", { className: "text-xs text-red-600", children: "Send failed \u2014 check backend connection." })), _jsxs("div", { className: "border-t border-red-100 pt-3", children: [_jsx("p", { className: "text-xs text-gray-400 mb-2", children: "Or mark as resolved without sending a reply:" }), _jsxs("div", { className: "space-y-2", children: [_jsx("input", { type: "text", value: resolveNotes, onChange: e => setResolveNotes(e.target.value), placeholder: "Review notes (optional)\u2026", className: "w-full text-sm border border-red-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-red-300 bg-white" }), _jsxs("button", { onClick: () => resolve.mutate({ id: email.id, notes: resolveNotes || undefined }), disabled: resolve.isPending, className: "flex items-center gap-1.5 text-sm text-white bg-red-600 hover:bg-red-700 disabled:opacity-60 px-4 py-1.5 rounded-lg transition-colors font-medium", children: [resolve.isPending ? _jsx(LoadingSpinner, { size: "sm" }) : _jsx(CheckCircle, { size: 13 }), resolve.isPending ? 'Resolving…' : 'Mark Resolved (no reply)'] }), resolve.isError && (_jsx("p", { className: "text-xs text-red-600", children: "Failed to resolve \u2014 try again." }))] })] })] }))] }));
    }
    // ── Normal draft (not escalated, not replied) ─────────────
    return (_jsxs("div", { className: "border rounded-xl bg-white overflow-hidden", children: [_jsxs("div", { className: "flex items-center justify-between px-4 py-3 border-b bg-gray-50", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx(Cpu, { size: 15, className: "text-blue-600" }), _jsx("span", { className: "text-sm font-medium text-gray-800", children: "AI Draft" }), draft.tone_used && (_jsxs("span", { className: "text-xs text-gray-400 capitalize", children: ["\u00B7 ", draft.tone_used, " tone"] }))] }), confidence != null && (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "w-24 h-1.5 bg-gray-200 rounded-full overflow-hidden", children: _jsx("div", { className: `h-full rounded-full transition-all ${confColor}`, style: { width: `${confidence}%` } }) }), _jsxs("span", { className: `text-xs font-medium ${confidence >= 80 ? 'text-green-600' :
                                    confidence >= 60 ? 'text-yellow-600' :
                                        'text-red-600'}`, children: [Math.round(confidence), "%"] })] }))] }), _jsx("div", { className: "p-4", children: isEditing ? (_jsx("textarea", { value: editedText, onChange: e => setEditedText(e.target.value), rows: 8, className: "w-full text-sm text-gray-700 border border-blue-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none leading-relaxed", autoFocus: true })) : (_jsx("p", { className: "text-sm text-gray-700 whitespace-pre-wrap leading-relaxed min-h-[80px]", children: editedText })) }), _jsxs("div", { className: "flex items-center justify-between px-4 py-3 border-t bg-gray-50 gap-2 flex-wrap", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("button", { onClick: () => setIsEditing(v => !v), className: "flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 bg-white hover:bg-gray-50 px-3 py-1.5 rounded-lg transition-colors", children: isEditing ? _jsxs(_Fragment, { children: [_jsx(RotateCcw, { size: 13 }), " Cancel"] }) : _jsxs(_Fragment, { children: [_jsx(Edit3, { size: 13 }), " Edit"] }) }), _jsxs("button", { onClick: () => escalate.mutate(email.id), disabled: escalate.isPending, className: "flex items-center gap-1.5 text-sm text-red-600 hover:text-red-700 border border-red-200 bg-red-50 hover:bg-red-100 disabled:opacity-60 px-3 py-1.5 rounded-lg transition-colors", children: [escalate.isPending ? _jsx(LoadingSpinner, { size: "sm" }) : _jsx(AlertTriangle, { size: 13 }), "Escalate"] })] }), _jsxs("button", { onClick: () => approve.mutate(email.id), disabled: approve.isPending, className: "flex items-center gap-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60 px-4 py-1.5 rounded-lg transition-colors font-medium", children: [approve.isPending ? _jsx(LoadingSpinner, { size: "sm" }) : _jsx(CheckCircle, { size: 13 }), approve.isPending ? 'Sending…' : 'Approve & Send'] })] }), (approve.isError || escalate.isError) && (_jsx("div", { className: "px-4 pb-3 text-xs text-red-600", children: "Action failed \u2014 check backend connection." }))] }));
}
