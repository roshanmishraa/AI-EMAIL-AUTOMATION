import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
const COLORS = {
    legal: '#ef4444',
    billing: '#eab308',
    product_issue: '#a855f7',
    delivery: '#6366f1',
    refund: '#ec4899',
    general: '#9ca3af',
    spam: '#64748b',
    feedback: '#14b8a6',
};
const ICONS = {
    legal: '⚖️',
    billing: '💳',
    product_issue: '🔧',
    delivery: '📦',
    refund: '↩️',
    general: '✉️',
    spam: '🚫',
    feedback: '⭐',
};
const cleanKey = (raw) => raw.replace('EmailCategory.', '').replace('EmailSentiment.', '');
export default function CategoryPie({ distribution }) {
    const data = Object.entries(distribution)
        .filter(([, v]) => v > 0)
        .map(([name, value]) => {
        const key = cleanKey(name);
        return {
            name: `${ICONS[key] ?? ''} ${key.replace('_', ' ')}`,
            key,
            value,
        };
    });
    if (data.length === 0) {
        return (_jsx("div", { className: "flex items-center justify-center h-48 text-gray-400 text-sm", children: "No category data yet" }));
    }
    return (_jsx(ResponsiveContainer, { width: "100%", height: 240, children: _jsxs(PieChart, { children: [_jsx(Pie, { data: data, cx: "50%", cy: "50%", innerRadius: 55, outerRadius: 90, paddingAngle: 3, dataKey: "value", children: data.map((entry) => (_jsx(Cell, { fill: COLORS[entry.key] ?? '#9ca3af' }, entry.key))) }), _jsx(Tooltip, { formatter: (value, name) => [value, name], contentStyle: { fontSize: 12, borderRadius: 8 } }), _jsx(Legend, { iconType: "circle", iconSize: 8, wrapperStyle: { fontSize: 11 } })] }) }));
}
