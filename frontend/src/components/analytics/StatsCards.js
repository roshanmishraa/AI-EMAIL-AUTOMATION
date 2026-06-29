import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Mail, CheckCircle, AlertTriangle, Zap } from 'lucide-react';
const cards = (s) => [
    {
        label: 'Total Emails',
        value: s.total_emails,
        icon: Mail,
        color: 'text-blue-600',
        bg: 'bg-blue-50',
    },
    {
        label: 'Auto Replied',
        value: s.replied,
        icon: CheckCircle,
        color: 'text-green-600',
        bg: 'bg-green-50',
    },
    {
        label: 'Escalated',
        value: s.escalated,
        icon: AlertTriangle,
        color: 'text-red-600',
        bg: 'bg-red-50',
    },
    {
        label: 'Avg Confidence',
        value: `${Math.round(s.avg_confidence)}%`,
        icon: Zap,
        color: s.avg_confidence >= 80 ? 'text-green-600' : s.avg_confidence >= 60 ? 'text-yellow-600' : 'text-red-600',
        bg: s.avg_confidence >= 80 ? 'bg-green-50' : s.avg_confidence >= 60 ? 'bg-yellow-50' : 'bg-red-50',
    },
];
export default function StatsCards({ stats }) {
    return (_jsx("div", { className: "grid grid-cols-2 lg:grid-cols-4 gap-4", children: cards(stats).map(card => (_jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsxs("div", { className: "flex items-center justify-between mb-3", children: [_jsx("span", { className: "text-sm text-gray-500", children: card.label }), _jsx("div", { className: `w-8 h-8 rounded-lg ${card.bg} flex items-center justify-center`, children: _jsx(card.icon, { size: 16, className: card.color }) })] }), _jsx("div", { className: `text-2xl font-bold ${card.color}`, children: card.value })] }, card.label))) }));
}
