import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// ============================================================
// FILE:  frontend/src/pages/EmailDetailPage.tsx
// FIX:   Spam emails ke liye KB Sources card hide kiya
//        + spam pe fetchChunksForEmail API call bhi nahi hogi
// ============================================================
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ExternalLink, BookOpen } from 'lucide-react';
import { useEmail } from '../hooks/useEmails';
import { useQuery } from '@tanstack/react-query';
import Topbar from '../components/layout/Topbar';
import AIReplyPanel from '../components/inbox/AIReplyPanel';
import ThreadView from '../components/inbox/ThreadView';
import Badge from '../components/common/Badge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ChunkPreview from '../components/kb/ChunkPreview';
import { formatDateTime } from '../types/date';
import client from '../api/axiosClient';
import { fetchChunksForEmail } from '../api/kbApi';
export default function EmailDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const emailId = Number(id);
    const { data: email, isLoading, isError } = useEmail(emailId);
    // Fetch thread messages
    const { data: threadData } = useQuery({
        queryKey: ['thread', email?.thread_id],
        queryFn: () => client.get(`/emails/thread/${email.thread_id}`).then(r => r.data),
        enabled: !!email?.thread_id,
        select: d => d.emails ?? [],
    });
    // Fetch KB chunks — spam pe disabled:
    // 1. Spam ka RAG retrieval backend pe hota hi nahi (ai_processor early exit)
    // 2. rag.py mein bhi SKIP_RAG_CATEGORIES guard hai
    // 3. Frontend pe bhi API call skip — no wasted network request
    const isSpam = email?.category === 'spam';
    const { data: chunkData, isLoading: chunksLoading } = useQuery({
        queryKey: ['kb-chunks', emailId],
        queryFn: () => fetchChunksForEmail(emailId).then(r => r.data),
        enabled: !!email && !isSpam, // ← FIX: spam pe fetch hi nahi hogi
        staleTime: 5 * 60 * 1000,
    });
    const threadEmails = threadData ?? (email ? [email] : []);
    if (isLoading) {
        return (_jsx("div", { className: "flex items-center justify-center h-full", children: _jsx(LoadingSpinner, { size: "lg" }) }));
    }
    if (isError || !email) {
        return (_jsxs("div", { className: "flex flex-col items-center justify-center h-full gap-3", children: [_jsx("p", { className: "text-gray-500", children: "Email not found." }), _jsx("button", { onClick: () => navigate('/inbox'), className: "text-blue-600 text-sm hover:underline", children: "\u2190 Back to Inbox" })] }));
    }
    return (_jsxs("div", { className: "flex flex-col h-full", children: [_jsx(Topbar, { title: email.subject || '(no subject)', subtitle: `From: ${email.sender}`, actions: _jsxs("button", { onClick: () => navigate('/inbox'), className: "flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 bg-white px-3 py-1.5 rounded-lg", children: [_jsx(ArrowLeft, { size: 14 }), " Back"] }) }), _jsxs("div", { className: "flex-1 overflow-auto p-6 grid grid-cols-3 gap-6 items-start", children: [_jsxs("div", { className: "col-span-2 flex flex-col gap-5", children: [_jsxs("div", { className: "border rounded-xl bg-white overflow-hidden", children: [_jsxs("div", { className: "px-5 py-4 border-b bg-gray-50 flex items-center justify-between", children: [_jsxs("div", { children: [_jsx("p", { className: "text-sm font-medium text-gray-800", children: email.sender }), _jsx("p", { className: "text-xs text-gray-400 mt-0.5", children: formatDateTime(email.received_at) })] }), _jsxs("a", { href: `https://mail.google.com/mail/u/0/#inbox/${email.gmail_message_id}`, target: "_blank", rel: "noopener noreferrer", className: "text-xs text-gray-400 hover:text-blue-600 flex items-center gap-1", children: ["Open in Gmail ", _jsx(ExternalLink, { size: 11 })] })] }), _jsx("div", { className: "px-5 py-4", children: _jsx("p", { className: "text-sm text-gray-700 whitespace-pre-wrap leading-relaxed", children: email.body }) }), email.has_attachments && (_jsxs("div", { className: "px-5 py-3 border-t bg-amber-50 flex items-center gap-2", children: [_jsx("span", { className: "text-xs text-amber-700 font-medium", children: "\uD83D\uDCCE Attachments:" }), _jsx("span", { className: "text-xs text-amber-600", children: (() => {
                                                    try {
                                                        const names = JSON.parse(email.attachment_names || '[]');
                                                        return names.join(', ');
                                                    }
                                                    catch {
                                                        return 'attached files';
                                                    }
                                                })() })] }))] }), threadEmails.length > 1 && (_jsx(ThreadView, { emails: threadEmails, currentEmailId: emailId })), _jsxs("div", { children: [_jsx("h3", { className: "text-sm font-medium text-gray-700 mb-2", children: "AI Generated Reply" }), _jsx(AIReplyPanel, { email: email })] })] }), _jsxs("div", { className: "flex flex-col gap-4", children: [_jsxs("div", { className: "border rounded-xl bg-white p-4", children: [_jsx("p", { className: "text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3", children: "Status" }), _jsxs("div", { className: "flex flex-col gap-2.5", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsx("span", { className: "text-xs text-gray-500", children: "Status" }), _jsx(Badge, { label: email.status, variant: "status", value: email.status })] }), email.category && (_jsxs("div", { className: "flex items-center justify-between", children: [_jsx("span", { className: "text-xs text-gray-500", children: "Category" }), _jsx(Badge, { label: email.category.replace('_', ' '), variant: "category", value: email.category })] })), email.sentiment && (_jsxs("div", { className: "flex items-center justify-between", children: [_jsx("span", { className: "text-xs text-gray-500", children: "Sentiment" }), _jsx(Badge, { label: email.sentiment, variant: "sentiment", value: email.sentiment })] })), email.confidence_score != null && (_jsxs("div", { className: "flex items-center justify-between", children: [_jsx("span", { className: "text-xs text-gray-500", children: "AI Confidence" }), _jsxs("span", { className: `text-xs font-medium ${email.confidence_score >= 80 ? 'text-green-600' :
                                                            email.confidence_score >= 60 ? 'text-yellow-600' :
                                                                'text-red-600'}`, children: [Math.round(email.confidence_score), "%"] })] }))] })] }), _jsxs("div", { className: "border rounded-xl bg-white p-4", children: [_jsx("p", { className: "text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3", children: "Details" }), _jsxs("div", { className: "flex flex-col gap-2.5", children: [_jsxs("div", { children: [_jsx("p", { className: "text-xs text-gray-400", children: "Received" }), _jsx("p", { className: "text-xs text-gray-700 mt-0.5", children: formatDateTime(email.received_at) })] }), email.intent && (_jsxs("div", { children: [_jsx("p", { className: "text-xs text-gray-400", children: "Intent" }), _jsx("p", { className: "text-xs text-gray-700 mt-0.5 capitalize", children: email.intent.replace(/_/g, ' ') })] })), email.thread_id && (_jsxs("div", { children: [_jsx("p", { className: "text-xs text-gray-400", children: "Thread ID" }), _jsx("p", { className: "text-xs text-gray-500 mt-0.5 font-mono truncate", children: email.thread_id })] }))] })] }), email.replies?.length > 0 && (_jsxs("div", { className: "border rounded-xl bg-white p-4", children: [_jsxs("p", { className: "text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3", children: ["AI Drafts (", email.replies.length, ")"] }), email.replies.map((r, i) => (_jsxs("div", { className: "text-xs text-gray-500 py-1 border-b last:border-0 flex justify-between", children: [_jsxs("span", { children: ["Draft ", i + 1, " \u00B7 ", r.generated_by] }), _jsx("span", { className: r.is_approved ? 'text-green-600' : 'text-gray-400', children: r.is_approved ? '✓ Sent' : 'Pending' })] }, r.id)))] })), !isSpam && (_jsxs("div", { className: "border rounded-xl bg-white p-4", children: [_jsxs("div", { className: "flex items-center gap-1.5 mb-3", children: [_jsx(BookOpen, { size: 12, className: "text-gray-400" }), _jsx("p", { className: "text-xs font-semibold text-gray-400 uppercase tracking-wider", children: "KB Sources Used" })] }), chunksLoading && (_jsx("div", { className: "flex items-center justify-center py-4", children: _jsx(LoadingSpinner, { size: "sm" }) })), !chunksLoading && chunkData && (_jsx(_Fragment, { children: chunkData.chunks_found === 0 ? (_jsx("p", { className: "text-xs text-gray-400 italic", children: "No KB articles matched this email's category." })) : (_jsxs(_Fragment, { children: [_jsxs("p", { className: "text-[11px] text-gray-400 mb-2", children: [chunkData.chunks_found, " chunk", chunkData.chunks_found !== 1 ? 's' : '', " retrieved", chunkData.category ? ` for category: ${chunkData.category}` : ''] }), _jsx(ChunkPreview, { chunks: chunkData.chunks })] })) }))] }))] })] })] }));
}
