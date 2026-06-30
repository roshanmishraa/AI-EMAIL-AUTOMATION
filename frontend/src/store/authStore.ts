// ============================================================
// FILE:  frontend/src/store/authStore.ts
// CHANGE: logout() ab backend /auth/disconnect bhi call karta hai
//         Pehle sirf localStorage clear hota tha — backend ko pata
//         hi nahi chalta tha, isliye Celery poller is_active=True
//         user ko hamesha poll karta rehta tha "sign out" ke baad bhi.
// NEW: login() aur logout() dono ab queryClient.clear() bhi karte hain
//      taaki purane account ka cached React Query data naye account
//      ke saath mix na ho ya flash na ho.
// ============================================================

import { create } from 'zustand'
import { queryClient } from '../lib/queryClient'

// /auth/* routes backend mein /api/v1 prefix ke bina hain (main.py mein
// directly @app.get/@app.post) — isliye axiosClient (jo /api/v1 jodta hai)
// use nahi kar sakte. Yehi pattern LoginPage.tsx mein bhi /auth/gmail
// ke liye use hota hai.
const BACKEND_URL = import.meta.env.VITE_API_URL ?? ''

interface AuthState {
  userId:    number | null
  userEmail: string | null
  isLoggedIn: boolean

  login:  (userId: number, email: string) => void
  logout: () => Promise<void>
}

// localStorage se existing session restore karo
const savedUserId    = localStorage.getItem('user_id')
const savedUserEmail = localStorage.getItem('user_email')

export const useAuthStore = create<AuthState>(set => ({
  userId:    savedUserId    ? Number(savedUserId)  : null,
  userEmail: savedUserEmail ? savedUserEmail        : null,
  isLoggedIn: !!savedUserId,

  login: (userId, email) => {
    localStorage.setItem('user_id',    String(userId))
    localStorage.setItem('user_email', email)
    queryClient.clear()   // NEW: koi purana cached data carry-over na ho
    set({ userId, userEmail: email, isLoggedIn: true })
  },

  logout: async () => {
    const userId = localStorage.getItem('user_id')

    // Backend ko bata do account disconnect ho raha hai —
    // is_active=False set hoga, gmail_token clear hoga,
    // taaki Celery poller is account ko skip kare
    if (userId) {
      try {
        await fetch(`${BACKEND_URL}/auth/disconnect?user_id=${userId}`, {
          method: 'POST',
        })
      } catch (e) {
        // Backend call fail bhi ho jaye, local logout fir bhi hona chahiye
        console.error('[Disconnect Error]', e)
      }
    }

    localStorage.removeItem('user_id')
    localStorage.removeItem('user_email')
    queryClient.clear()   // NEW: purana account ka cached data hata do
    set({ userId: null, userEmail: null, isLoggedIn: false })
  },
}))