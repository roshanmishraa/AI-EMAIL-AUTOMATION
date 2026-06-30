// ============================================================
// FILE:  frontend/src/lib/queryClient.ts
// NEW FILE: queryClient ko ek shared module mein nikala hai
//           taaki authStore.ts (logout pe cache clear karne ke liye)
//           aur main.tsx (Provider ke liye) dono isi instance ko
//           import kar sakein — pehle ye sirf main.tsx ke andar
//           inline banta tha, isliye bahar se access nahi tha.
// ============================================================
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient()