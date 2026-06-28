// ============================================================
// FILE:  frontend/src/App.tsx
// CHANGE: Auth routing add kiya
//         - Login page add kiya
//         - Protected routes — login nahi toh /login pe redirect
//         - Logout button Sidebar mein dikhega (Sidebar.tsx se handle hoga)
// ============================================================

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import InboxPage from './pages/InboxPage'
import EmailDetailPage from './pages/EmailDetailPage'
import AnalyticsPage from './pages/AnalyticsPage'
import KBManagerPage from './pages/KBManagerPage'
import SettingsPage from './pages/SettingsPage'
import LoginPage from './pages/LoginPage'
import { useAuthStore } from './store/authStore'

// ── Protected Route wrapper ───────────────────────────────────
// Agar user logged in nahi hai toh /login pe bhejo
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoggedIn } = useAuthStore()
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

// ── App layout (sidebar + main content) ─────────────────────
function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Public route — login page */}
        <Route path="/login" element={<LoginPage />} />

        {/* Protected routes — login chahiye */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppLayout>
                <Navigate to="/inbox" replace />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/inbox"
          element={
            <ProtectedRoute>
              <AppLayout>
                <InboxPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/inbox/:id"
          element={
            <ProtectedRoute>
              <AppLayout>
                <EmailDetailPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <AppLayout>
                <AnalyticsPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/kb"
          element={
            <ProtectedRoute>
              <AppLayout>
                <KBManagerPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <AppLayout>
                <SettingsPage />
              </AppLayout>
            </ProtectedRoute>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/inbox" replace />} />

      </Routes>
    </BrowserRouter>
  )
}
