import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
// ============================================================
// FILE:  frontend/src/App.tsx
// CHANGE: Auth routing add kiya
//         - Login page add kiya
//         - Protected routes — login nahi toh /login pe redirect
//         - Logout button Sidebar mein dikhega (Sidebar.tsx se handle hoga)
// ============================================================
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import InboxPage from './pages/InboxPage';
import EmailDetailPage from './pages/EmailDetailPage';
import AnalyticsPage from './pages/AnalyticsPage';
import KBManagerPage from './pages/KBManagerPage';
import SettingsPage from './pages/SettingsPage';
import LoginPage from './pages/LoginPage';
import { useAuthStore } from './store/authStore';
// ── Protected Route wrapper ───────────────────────────────────
// Agar user logged in nahi hai toh /login pe bhejo
function ProtectedRoute({ children }) {
    const { isLoggedIn } = useAuthStore();
    if (!isLoggedIn) {
        return _jsx(Navigate, { to: "/login", replace: true });
    }
    return _jsx(_Fragment, { children: children });
}
// ── App layout (sidebar + main content) ─────────────────────
function AppLayout({ children }) {
    return (_jsxs("div", { className: "flex h-screen bg-gray-50", children: [_jsx(Sidebar, {}), _jsx("main", { className: "flex-1 overflow-auto", children: children })] }));
}
export default function App() {
    return (_jsx(BrowserRouter, { children: _jsxs(Routes, { children: [_jsx(Route, { path: "/login", element: _jsx(LoginPage, {}) }), _jsx(Route, { path: "/", element: _jsx(ProtectedRoute, { children: _jsx(AppLayout, { children: _jsx(Navigate, { to: "/inbox", replace: true }) }) }) }), _jsx(Route, { path: "/inbox", element: _jsx(ProtectedRoute, { children: _jsx(AppLayout, { children: _jsx(InboxPage, {}) }) }) }), _jsx(Route, { path: "/inbox/:id", element: _jsx(ProtectedRoute, { children: _jsx(AppLayout, { children: _jsx(EmailDetailPage, {}) }) }) }), _jsx(Route, { path: "/analytics", element: _jsx(ProtectedRoute, { children: _jsx(AppLayout, { children: _jsx(AnalyticsPage, {}) }) }) }), _jsx(Route, { path: "/kb", element: _jsx(ProtectedRoute, { children: _jsx(AppLayout, { children: _jsx(KBManagerPage, {}) }) }) }), _jsx(Route, { path: "/settings", element: _jsx(ProtectedRoute, { children: _jsx(AppLayout, { children: _jsx(SettingsPage, {}) }) }) }), _jsx(Route, { path: "*", element: _jsx(Navigate, { to: "/inbox", replace: true }) })] }) }));
}
