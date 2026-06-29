import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// ============================================================
// FILE:  frontend/src/components/layout/Sidebar.tsx
// CHANGE: User email + Logout button add kiya footer mein
// ============================================================
import { NavLink, useNavigate } from 'react-router-dom';
import { Mail, BarChart2, BookOpen, Settings, Zap, LogOut } from 'lucide-react';
import { useUnreadCount } from '../../hooks/useNotifications';
import { useAuthStore } from '../../store/authStore';
const links = [
    { to: '/inbox', icon: Mail, label: 'Inbox' },
    { to: '/analytics', icon: BarChart2, label: 'Analytics' },
    { to: '/kb', icon: BookOpen, label: 'Knowledge Base' },
    { to: '/settings', icon: Settings, label: 'Settings' },
];
export default function Sidebar() {
    const { unreadCount } = useUnreadCount();
    const { userEmail, logout } = useAuthStore();
    const navigate = useNavigate();
    const handleLogout = () => {
        logout();
        navigate('/login', { replace: true });
    };
    return (_jsxs("aside", { className: "w-60 border-r bg-white flex flex-col py-6 px-3 gap-1 shrink-0", children: [_jsxs("div", { className: "px-3 pb-5 flex items-center gap-2", children: [_jsx("div", { className: "w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center", children: _jsx(Zap, { size: 14, className: "text-white" }) }), _jsxs("div", { children: [_jsx("div", { className: "text-sm font-bold text-gray-900", children: "AI Email" }), _jsx("div", { className: "text-xs text-gray-400", children: "Automation" })] })] }), _jsx("div", { className: "text-[10px] font-semibold text-gray-400 uppercase tracking-widest px-3 pb-1", children: "Navigation" }), links.map(({ to, icon: Icon, label }) => (_jsxs(NavLink, { to: to, className: ({ isActive }) => `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${isActive
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`, children: [_jsx(Icon, { size: 16 }), _jsx("span", { className: "flex-1", children: label }), to === '/inbox' && unreadCount > 0 && (_jsx("span", { className: "\r\n              inline-flex items-center justify-center\r\n              min-w-[18px] h-[18px] px-1\r\n              text-[10px] font-semibold\r\n              bg-red-500 text-white\r\n              rounded-full leading-none\r\n            ", children: unreadCount > 99 ? '99+' : unreadCount }))] }, to))), _jsxs("div", { className: "mt-auto px-3 pt-4 border-t space-y-3", children: [userEmail && (_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("div", { className: "w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center shrink-0", children: _jsx("span", { className: "text-xs font-semibold text-blue-700", children: userEmail[0].toUpperCase() }) }), _jsxs("div", { className: "flex-1 min-w-0", children: [_jsx("p", { className: "text-xs font-medium text-gray-700 truncate", children: userEmail }), _jsx("p", { className: "text-[10px] text-green-500 font-medium", children: "\u25CF Connected" })] })] })), _jsxs("button", { onClick: handleLogout, className: "\r\n            w-full flex items-center gap-2 px-2 py-2 rounded-lg\r\n            text-xs text-gray-500 hover:text-red-600 hover:bg-red-50\r\n            transition-colors\r\n          ", children: [_jsx(LogOut, { size: 13 }), "Sign out"] })] })] }));
}
