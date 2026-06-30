// ============================================================
// FILE:  frontend/src/hooks/useAnalytics.ts
// CHANGE: userId ko queryKey mein add kiya — taaki alag account ka
//         dashboard data cache mix na ho.
// ============================================================
import { useQuery } from '@tanstack/react-query'
import { getDashboard } from '../api/analyticsApi'
import { useAuthStore } from '../store/authStore'

export const useAnalytics = () => {
  const userId = useAuthStore(s => s.userId)
  return useQuery({
    queryKey: ['dashboard', userId],
    queryFn: getDashboard,
    select: res => res.data,
    refetchInterval: 60000,
    enabled: !!userId,
  })
}