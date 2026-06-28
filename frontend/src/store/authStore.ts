// ============================================================
// FILE:  frontend/src/store/authStore.ts
// NEW FILE: User login state manage karne ke liye
//           localStorage mein user_id + email store hota hai
//           taaki page refresh pe bhi login rahe
// ============================================================

import { create } from 'zustand'

interface AuthState {
  userId:    number | null
  userEmail: string | null
  isLoggedIn: boolean

  login:  (userId: number, email: string) => void
  logout: () => void
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
    set({ userId, userEmail: email, isLoggedIn: true })
  },

  logout: () => {
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_email')
    set({ userId: null, userEmail: null, isLoggedIn: false })
  },
}))