import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { BookOpen } from 'lucide-react';
export default function ChunkPreview({ chunks }) {
    if (!chunks || chunks.length === 0) {
        return (_jsx("div", { className: "text-xs text-gray-400 italic", children: "No chunks to preview." }));
    }
    return (_jsx("div", { className: "space-y-2 max-h-64 overflow-y-auto", children: chunks.map((chunk, i) => (_jsxs("div", { className: "bg-gray-50 border border-gray-100 rounded-lg px-3 py-2", children: [_jsxs("div", { className: "flex items-center gap-1.5 mb-1", children: [_jsx(BookOpen, { size: 10, className: "text-gray-400" }), _jsxs("span", { className: "text-[10px] text-gray-400 font-medium uppercase tracking-wide", children: ["Chunk ", i + 1] })] }), _jsx("p", { className: "text-xs text-gray-600 leading-relaxed line-clamp-3", children: chunk })] }, i))) }));
}
