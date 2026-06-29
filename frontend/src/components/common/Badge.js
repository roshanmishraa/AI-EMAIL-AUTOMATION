import { jsx as _jsx } from "react/jsx-runtime";
const sentimentColors = {
    angry: 'bg-red-100 text-red-700 border border-red-200',
    frustrated: 'bg-orange-100 text-orange-700 border border-orange-200',
    neutral: 'bg-gray-100 text-gray-600 border border-gray-200',
    happy: 'bg-green-100 text-green-700 border border-green-200',
    sad: 'bg-blue-100 text-blue-700 border border-blue-200',
};
const categoryColors = {
    legal: 'bg-red-50 text-red-700 border border-red-200',
    billing: 'bg-yellow-50 text-yellow-700 border border-yellow-200',
    product_issue: 'bg-purple-50 text-purple-700 border border-purple-200',
    delivery: 'bg-indigo-50 text-indigo-700 border border-indigo-200',
    refund: 'bg-pink-50 text-pink-700 border border-pink-200',
    general: 'bg-gray-50 text-gray-600 border border-gray-200',
    spam: 'bg-slate-50 text-slate-500 border border-slate-200',
    feedback: 'bg-teal-50 text-teal-700 border border-teal-200',
};
const statusColors = {
    new: 'bg-blue-100 text-blue-700 border border-blue-200',
    processing: 'bg-yellow-100 text-yellow-700 border border-yellow-200',
    processed: 'bg-purple-100 text-purple-700 border border-purple-200',
    replied: 'bg-green-100 text-green-700 border border-green-200',
    escalated: 'bg-red-100 text-red-700 border border-red-200',
};
const categoryIcons = {
    legal: '⚖️', billing: '💳', product_issue: '🔧',
    delivery: '📦', refund: '↩️', general: '✉️', spam: '🚫', feedback: '⭐',
};
const sentimentIcons = {
    angry: '😡', frustrated: '😤', neutral: '😐', happy: '😊', sad: '😢',
};
export default function Badge({ label, variant = 'default', value }) {
    let cls = 'bg-gray-100 text-gray-600 border border-gray-200';
    let display = label;
    if (variant === 'sentiment' && value) {
        cls = sentimentColors[value] ?? cls;
        display = `${sentimentIcons[value] ?? ''} ${label}`;
    }
    else if (variant === 'category' && value) {
        cls = categoryColors[value] ?? cls;
        display = `${categoryIcons[value] ?? ''} ${label}`;
    }
    else if (variant === 'status' && value) {
        cls = statusColors[value] ?? cls;
    }
    return (_jsx("span", { className: `inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${cls}`, children: display }));
}
