import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useAnalytics } from '../hooks/useAnalytics';
import Topbar from '../components/layout/Topbar';
import StatsCards from '../components/analytics/StatsCards';
import CategoryPie from '../components/analytics/CategoryPie';
import SentimentChart from '../components/analytics/SentimentChart';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
// ── Escalation reason → human readable label ──
const REASON_LABELS = {
    legal: 'Legal',
    low_confidence: 'Low Confidence',
    angry_repeat: 'Angry Repeat',
    vip: 'VIP Customer',
    sensitive_attachment: 'Sensitive Attachment',
};
// ── Sentiment → color for trend chart ──
const SENTIMENT_COLORS = {
    angry: '#ef4444',
    frustrated: '#f97316',
    neutral: '#6b7280',
    happy: '#22c55e',
    sad: '#3b82f6',
};
// ── Format seconds → "2m 30s" or "45s" ──
function formatResponseTime(seconds) {
    if (seconds === null || seconds === undefined)
        return '—';
    if (seconds < 60)
        return `${Math.round(seconds)}s`;
    const m = Math.floor(seconds / 60);
    const s = Math.round(seconds % 60);
    return s > 0 ? `${m}m ${s}s` : `${m}m`;
}
export default function AnalyticsPage() {
    const { data: stats, isLoading, isError } = useAnalytics();
    // ── Build sentiment trend data for recharts ──
    const trendChartData = stats?.sentiment_trend.map((point) => {
        const label = new Date(point.date).toLocaleDateString('en-IN', {
            month: 'short', day: 'numeric',
        });
        return { date: label, ...point.sentiment_counts };
    }) ?? [];
    // ── All unique sentiments across trend data (for Bar keys) ──
    const trendSentiments = Array.from(new Set(trendChartData.flatMap(d => Object.keys(d).filter(k => k !== 'date'))));
    return (_jsxs("div", { className: "flex flex-col h-full", children: [_jsx(Topbar, { title: "Analytics", subtitle: "Email pipeline overview" }), _jsxs("div", { className: "flex-1 overflow-auto p-6 space-y-6", children: [isLoading && (_jsx("div", { className: "flex items-center justify-center h-48", children: _jsx(LoadingSpinner, { size: "lg" }) })), isError && (_jsx("div", { className: "px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700", children: "Failed to load analytics \u2014 check backend connection." })), stats && (_jsxs(_Fragment, { children: [_jsx(StatsCards, { stats: stats }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsx("h2", { className: "text-sm font-semibold text-gray-700 mb-4", children: "Category Breakdown" }), _jsx(CategoryPie, { distribution: stats.category_distribution })] }), _jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsx("h2", { className: "text-sm font-semibold text-gray-700 mb-4", children: "Sentiment Distribution" }), _jsx(SentimentChart, { distribution: stats.sentiment_distribution })] })] }), _jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsx("h2", { className: "text-sm font-semibold text-gray-700 mb-4", children: "Pipeline Status" }), _jsx("div", { className: "grid grid-cols-3 gap-4", children: [
                                            { label: 'Processed', value: stats.processed, color: 'text-purple-600', bg: 'bg-purple-50' },
                                            { label: 'Replied', value: stats.replied, color: 'text-green-600', bg: 'bg-green-50' },
                                            { label: 'Escalated', value: stats.escalated, color: 'text-red-600', bg: 'bg-red-50' },
                                        ].map(item => (_jsxs("div", { className: `rounded-xl p-4 ${item.bg}`, children: [_jsx("p", { className: "text-xs text-gray-500 mb-1", children: item.label }), _jsx("p", { className: `text-2xl font-bold ${item.color}`, children: item.value }), _jsx("p", { className: "text-xs text-gray-400 mt-1", children: stats.total_emails > 0
                                                        ? `${Math.round((item.value / stats.total_emails) * 100)}% of total`
                                                        : '—' })] }, item.label))) })] }), _jsxs("div", { className: "grid grid-cols-1 lg:grid-cols-2 gap-6", children: [_jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsx("h2", { className: "text-sm font-semibold text-gray-700 mb-4", children: "Avg Response Time" }), _jsxs("div", { className: "flex flex-col items-center justify-center h-32 gap-1", children: [_jsx("p", { className: "text-4xl font-bold text-indigo-600", children: formatResponseTime(stats.avg_response_time_seconds) }), _jsx("p", { className: "text-xs text-gray-400", children: "from email received \u2192 AI reply generated" }), stats.avg_response_time_seconds === null && (_jsx("p", { className: "text-xs text-gray-400 italic mt-1", children: "No replies sent yet" }))] })] }), _jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsx("h2", { className: "text-sm font-semibold text-gray-700 mb-4", children: "Top Escalation Reasons" }), Object.keys(stats.escalation_reasons).length === 0 ? (_jsx("p", { className: "text-sm text-gray-400 italic", children: "No escalations yet." })) : (_jsx("div", { className: "space-y-2", children: Object.entries(stats.escalation_reasons)
                                                    .sort(([, a], [, b]) => b - a)
                                                    .map(([reason, count]) => {
                                                    const pct = stats.escalated > 0
                                                        ? Math.round((count / stats.escalated) * 100)
                                                        : 0;
                                                    return (_jsxs("div", { children: [_jsxs("div", { className: "flex justify-between text-xs text-gray-600 mb-0.5", children: [_jsx("span", { children: REASON_LABELS[reason] ?? reason }), _jsx("span", { className: "font-semibold", children: count })] }), _jsx("div", { className: "w-full bg-gray-100 rounded-full h-1.5", children: _jsx("div", { className: "bg-red-400 h-1.5 rounded-full transition-all", style: { width: `${pct}%` } }) })] }, reason));
                                                }) }))] })] }), _jsxs("div", { className: "bg-white border border-gray-100 rounded-xl p-5 shadow-sm", children: [_jsx("h2", { className: "text-sm font-semibold text-gray-700 mb-4", children: "Sentiment Trend \u2014 Last 7 Days" }), trendChartData.length === 0 || trendSentiments.length === 0 ? (_jsx("p", { className: "text-sm text-gray-400 italic", children: "Not enough data yet." })) : (_jsx(ResponsiveContainer, { width: "100%", height: 220, children: _jsxs(BarChart, { data: trendChartData, barCategoryGap: "30%", children: [_jsx(XAxis, { dataKey: "date", tick: { fontSize: 11, fill: '#6b7280' }, axisLine: false, tickLine: false }), _jsx(YAxis, { allowDecimals: false, tick: { fontSize: 11, fill: '#6b7280' }, axisLine: false, tickLine: false }), _jsx(Tooltip, { contentStyle: { fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' } }), _jsx(Legend, { wrapperStyle: { fontSize: 11, paddingTop: 8 }, formatter: (val) => val.charAt(0).toUpperCase() + val.slice(1) }), trendSentiments.map((sentiment) => (_jsx(Bar, { dataKey: sentiment, stackId: "sentiment", fill: SENTIMENT_COLORS[sentiment] ?? '#94a3b8', radius: (sentiment === trendSentiments[trendSentiments.length - 1]
                                                        ? [4, 4, 0, 0]
                                                        : [0, 0, 0, 0]) }, sentiment)))] }) }))] })] }))] })] }));
}
