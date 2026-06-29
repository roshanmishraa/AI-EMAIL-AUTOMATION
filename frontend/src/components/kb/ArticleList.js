import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { Trash2, FileText, } from 'lucide-react';
import { formatDistanceToNow } from '../../types/date';
const ICON_MAP = {
    pdf: '📄',
    docx: '📝',
    txt: '📃',
    md: '📃',
};
export default function ArticleList({ docs, onDelete, isDeleting }) {
    if (docs.length === 0) {
        return (_jsxs("div", { className: "flex flex-col items-center justify-center py-20 text-center", children: [_jsx(FileText, { size: 40, className: "text-gray-200 mb-3" }), _jsx("p", { className: "text-gray-500 font-medium", children: "No KB articles yet" }), _jsx("p", { className: "text-gray-400 text-sm mt-1", children: "Upload PDF, DOCX, or TXT files to ground AI replies in your company knowledge." })] }));
    }
    return (_jsx("div", { className: "space-y-3", children: docs.map(doc => (_jsxs("div", { className: "bg-white border border-gray-100 rounded-xl px-5 py-4 shadow-sm flex items-center gap-4", children: [_jsx("div", { className: "text-2xl w-8 text-center shrink-0", children: ICON_MAP[doc.source_type?.toLowerCase() ?? ''] ?? '📄' }), _jsxs("div", { className: "flex-1 min-w-0", children: [_jsx("p", { className: "text-sm font-medium text-gray-900 truncate", children: doc.title }), _jsxs("div", { className: "flex items-center gap-3 mt-0.5", children: [_jsx("span", { className: "text-xs text-gray-400 uppercase tracking-wide", children: doc.source_type }), _jsx("span", { className: "text-xs text-gray-400", children: "\u00B7" }), _jsxs("span", { className: "text-xs text-gray-500", children: [doc.chunk_count, " chunks indexed"] }), doc.created_at && (_jsxs(_Fragment, { children: [_jsx("span", { className: "text-xs text-gray-400", children: "\u00B7" }), _jsx("span", { className: "text-xs text-gray-400", children: formatDistanceToNow(doc.created_at) })] }))] })] }), _jsx("div", { className: "shrink-0", children: _jsx("button", { onClick: () => onDelete(doc.id), disabled: isDeleting, className: "text-gray-400 hover:text-red-600 disabled:opacity-40 p-1.5 rounded-lg hover:bg-red-50 transition-colors", title: "Delete article", children: _jsx(Trash2, { size: 14 }) }) })] }, doc.id))) }));
}
