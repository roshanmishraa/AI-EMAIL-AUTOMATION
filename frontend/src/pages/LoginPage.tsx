// ============================================================
// FILE:  frontend/src/pages/LoginPage.tsx
// NEW FILE: Gmail OAuth login page
//           - "Login with Gmail" button → backend /auth/gmail → Google
//           - Callback URL se auth=success parse karke user save karo
//           - Production mein VITE_API_BASE_URL use karta hai
// ============================================================

import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Zap, Mail, ShieldCheck, Loader2 } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

// Local dev: /auth/gmail (vite proxy se backend pe)
// Production: https://your-backend.railway.app/auth/gmail
const BACKEND_URL = import.meta.env.VITE_API_URL ?? ''

export default function LoginPage() {
  const navigate                  = useNavigate()
  const [params]                  = useSearchParams()
  const { login, isLoggedIn }     = useAuthStore()
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState<string | null>(null)

  // ── Already logged in → inbox pe redirect karo ──────────
  useEffect(() => {
    if (isLoggedIn) {
      navigate('/inbox', { replace: true })
    }
  }, [isLoggedIn, navigate])

  // ── OAuth callback handle karo ───────────────────────────
  // Backend /oauth2callback ke baad yahan redirect aata hai:
  // /?auth=success&email=user@gmail.com&user_id=1
  useEffect(() => {
    const authStatus = params.get('auth')
    const email      = params.get('email')
    const userIdStr  = params.get('user_id')

    if (authStatus === 'success' && email && userIdStr) {
      login(Number(userIdStr), email)
      navigate('/inbox', { replace: true })
    } else if (authStatus === 'error') {
      setError('Google login failed. Please try again.')
      setLoading(false)
    }
  }, [params, login, navigate])

  // ── Gmail login button click ─────────────────────────────
  const handleGmailLogin = async () => {
    setLoading(true)
    setError(null)
    try {
      const res  = await fetch(`${BACKEND_URL}/auth/gmail`)
      const data = await res.json()
      // User ko Google login page pe bhejo
      window.location.href = data.auth_url
    } catch (e) {
      setError('Could not connect to server. Is the backend running?')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-sm border p-10 w-full max-w-md text-center">

        {/* Logo */}
        <div className="flex items-center justify-center gap-2.5 mb-8">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center">
            <Zap size={20} className="text-white" />
          </div>
          <div className="text-left">
            <div className="text-lg font-bold text-gray-900">AI Email Automation</div>
            <div className="text-xs text-gray-400">Smart support, powered by AI</div>
          </div>
        </div>

        {/* Heading */}
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Welcome back</h1>
        <p className="text-sm text-gray-500 mb-8">
          Connect your Gmail to start processing emails with AI
        </p>

        {/* Error */}
        {error && (
          <div className="mb-5 px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
            {error}
          </div>
        )}

        {/* Gmail Login Button */}
        <button
          onClick={handleGmailLogin}
          disabled={loading}
          className="
            w-full flex items-center justify-center gap-3
            bg-white border-2 border-gray-200 hover:border-blue-400
            hover:bg-blue-50 transition-all
            text-gray-700 font-medium text-sm
            py-3.5 px-5 rounded-xl
            disabled:opacity-60 disabled:cursor-not-allowed
          "
        >
          {loading ? (
            <Loader2 size={18} className="animate-spin text-blue-600" />
          ) : (
            <Mail size={18} className="text-red-500" />
          )}
          {loading ? 'Redirecting to Google...' : 'Continue with Gmail'}
        </button>

        {/* Features */}
        <div className="mt-8 space-y-2.5 text-left">
          {[
            'Auto-classify incoming emails by category',
            'AI-generated reply drafts with RAG',
            'Smart escalation for legal & urgent emails',
          ].map(text => (
            <div key={text} className="flex items-start gap-2.5">
              <ShieldCheck size={15} className="text-green-500 mt-0.5 shrink-0" />
              <span className="text-xs text-gray-500">{text}</span>
            </div>
          ))}
        </div>

        <p className="mt-8 text-[11px] text-gray-400">
          By continuing, you allow this app to read and send emails on your behalf.
          Your data is never shared.
        </p>
      </div>
    </div>
  )
}