import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, } from 'recharts';
const SENTIMENT_CONFIG = {
    angry: { color: '#ef4444', icon: '😡' },
    frustrated: { color: '#f97316', icon: '😤' },
    neutral: { color: '#9ca3af', icon: '😐' },
    happy: { color: '#22c55e', icon: '😊' },
    sad: { color: '#60a5fa', icon: '😢' },
};
const cleanKey = (raw) => raw.replace('EmailSentiment.', '').replace('EmailCategory.', '');
export default function SentimentChart({ distribution }) {
    const data = Object.entries(distribution)
        .filter(([, v]) => v > 0)
        .map(([raw, value]) => {
        const key = cleanKey(raw);
        return {
            key,
            name: `${SENTIMENT_CONFIG[key]?.icon ?? ''} ${key}`,
            value,
            color: SENTIMENT_CONFIG[key]?.color ?? '#9ca3af',
        };
    });
    if (data.length === 0) {
        return (_jsx("div", { className: "flex items-center justify-center h-48 text-gray-400 text-sm", children: "No sentiment data yet" }));
    }
    return (_jsx(ResponsiveContainer, { width: "100%", height: 240, children: _jsxs(BarChart, { data: data, barSize: 36, children: [_jsx(XAxis, { dataKey: "name", tick: { fontSize: 11, fill: '#6b7280' }, axisLine: false, tickLine: false }), _jsx(YAxis, { allowDecimals: false, tick: { fontSize: 11, fill: '#9ca3af' }, axisLine: false, tickLine: false }), _jsx(Tooltip, { cursor: { fill: '#f3f4f6' }, contentStyle: { fontSize: 12, borderRadius: 8 }, formatter: (value) => [value, 'Emails'] }), _jsx(Bar, { dataKey: "value", radius: [4, 4, 0, 0], children: data.map((entry) => (_jsx(Cell, { fill: entry.color }, entry.key))) })] }) }));
}
