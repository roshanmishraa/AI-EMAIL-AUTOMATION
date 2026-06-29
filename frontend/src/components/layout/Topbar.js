import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
export default function Topbar({ title, subtitle, actions }) {
    return (_jsxs("div", { className: "border-b bg-white px-6 py-4 flex items-center justify-between shrink-0", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-lg font-semibold text-gray-900", children: title }), subtitle && _jsx("p", { className: "text-sm text-gray-500 mt-0.5", children: subtitle })] }), actions && _jsx("div", { className: "flex items-center gap-2", children: actions })] }));
}
