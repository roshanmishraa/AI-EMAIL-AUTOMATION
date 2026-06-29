import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useRef } from 'react';
import { X, Upload, FileText } from 'lucide-react';
import LoadingSpinner from '../common/LoadingSpinner';
const CATEGORY_OPTIONS = [
    { value: '', label: 'No category (matches all)' },
    { value: 'legal', label: '⚖️  Legal' },
    { value: 'billing', label: '💳  Billing' },
    { value: 'product_issue', label: '🔧  Product Issue' },
    { value: 'delivery', label: '📦  Delivery' },
    { value: 'refund', label: '↩️  Refund' },
    { value: 'general', label: '✉️  General' },
    { value: 'feedback', label: '⭐  Feedback' },
];
export default function UploadModal({ onClose, onUpload, isUploading, error, }) {
    const [file, setFile] = useState(null);
    const [categoryTag, setCategoryTag] = useState('');
    const fileInputRef = useRef(null);
    const handleSubmit = async () => {
        if (!file)
            return;
        const form = new FormData();
        form.append('file', file);
        if (categoryTag)
            form.append('category_tag', categoryTag);
        await onUpload(form);
    };
    const handleDrop = (e) => {
        e.preventDefault();
        const dropped = e.dataTransfer.files[0];
        if (dropped)
            setFile(dropped);
    };
    return (_jsx("div", { className: "fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4", children: _jsxs("div", { className: "bg-white rounded-2xl shadow-xl w-full max-w-md", children: [_jsxs("div", { className: "flex items-center justify-between px-6 py-4 border-b", children: [_jsx("h2", { className: "text-base font-semibold text-gray-900", children: "Upload KB Article" }), _jsx("button", { onClick: onClose, className: "text-gray-400 hover:text-gray-600 p-1 rounded-lg hover:bg-gray-100 transition-colors", children: _jsx(X, { size: 16 }) })] }), _jsxs("div", { className: "p-6 space-y-4", children: [_jsxs("div", { className: `border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${file
                                ? 'border-blue-400 bg-blue-50'
                                : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'}`, onClick: () => fileInputRef.current?.click(), onDrop: handleDrop, onDragOver: (e) => e.preventDefault(), children: [_jsx("input", { ref: fileInputRef, type: "file", accept: ".pdf,.docx,.txt,.md", className: "hidden", onChange: (e) => e.target.files?.[0] && setFile(e.target.files[0]) }), file ? (_jsxs("div", { className: "flex items-center justify-center gap-2 text-blue-700", children: [_jsx(FileText, { size: 18 }), _jsx("span", { className: "text-sm font-medium", children: file.name })] })) : (_jsxs(_Fragment, { children: [_jsx(Upload, { size: 24, className: "text-gray-300 mx-auto mb-2" }), _jsxs("p", { className: "text-sm text-gray-500", children: ["Drag & drop or", ' ', _jsx("span", { className: "text-blue-600 font-medium", children: "browse" })] }), _jsx("p", { className: "text-xs text-gray-400 mt-1", children: "PDF, DOCX, TXT, MD" })] }))] }), _jsxs("div", { children: [_jsxs("label", { className: "block text-xs font-medium text-gray-600 mb-1.5", children: ["Category Tag", ' ', _jsx("span", { className: "text-gray-400 font-normal", children: "(optional \u2014 for precision RAG retrieval)" })] }), _jsx("select", { value: categoryTag, onChange: (e) => setCategoryTag(e.target.value), className: "w-full text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500", children: CATEGORY_OPTIONS.map((opt) => (_jsx("option", { value: opt.value, children: opt.label }, opt.value))) })] }), error && (_jsx("p", { className: "text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg", children: error }))] }), _jsxs("div", { className: "flex items-center justify-end gap-3 px-6 py-4 border-t", children: [_jsx("button", { onClick: onClose, className: "text-sm text-gray-600 hover:text-gray-900 border border-gray-200 px-4 py-2 rounded-lg transition-colors", children: "Cancel" }), _jsx("button", { onClick: handleSubmit, disabled: !file || isUploading, className: "flex items-center gap-2 text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60 px-4 py-2 rounded-lg transition-colors font-medium", children: isUploading ? (_jsxs(_Fragment, { children: [_jsx(LoadingSpinner, { size: "sm" }), " Uploading\u2026"] })) : (_jsxs(_Fragment, { children: [_jsx(Upload, { size: 14 }), " Upload"] })) })] })] }) }));
}
