// ============================================================
// FILE:  frontend/src/api/axiosClient.ts
// CHANGE: VITE_API_BASE_URL support add kiya
//         Local dev mein: /api/v1 (proxy se backend pe jaata hai)
//         Production mein: https://your-backend.railway.app/api/v1
// ============================================================

/// <reference types="vite/client" />
import axios from 'axios'

// Local dev: VITE_API_BASE_URL nahi hoga → relative URL use hoga (proxy kaam karega)
// Production: VITE_API_BASE_URL=https://your-backend.railway.app → direct call
const BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1'

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    'X-API-Key': import.meta.env.VITE_API_KEY ?? 'supersecret-change-me',
  },
})

// NEW: har request ke saath logged-in user_id automatically bhejo
// Pehle koi bhi request user_id nahi bhejti thi, isliye backend
// sabka data mix karke deta tha (Inbox/Analytics dynamic nahi the)
client.interceptors.request.use(config => {
  const userId = localStorage.getItem('user_id')
  if (userId) {
    config.params = { ...config.params, user_id: Number(userId) }
  }
  return config
})

client.interceptors.response.use(
  res => res,
  err => {
    console.error('[API Error]', err.response?.status, err.response?.data)
    return Promise.reject(err)
  }
)

export default client