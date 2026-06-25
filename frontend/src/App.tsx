import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import InboxPage from './pages/InboxPage'
import EmailDetailPage from './pages/EmailDetailPage'
import AnalyticsPage from './pages/AnalyticsPage'
import KBManagerPage from './pages/KBManagerPage'
import SettingsPage from './pages/SettingsPage'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/inbox" />} />
            <Route path="/inbox" element={<InboxPage />} />
            <Route path="/inbox/:id" element={<EmailDetailPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/kb" element={<KBManagerPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
