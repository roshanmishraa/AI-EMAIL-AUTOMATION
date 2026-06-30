// ============================================================
// FILE:  frontend/src/hooks/useNotifications.ts
// CHANGE: userId ko queryKey mein add kiya aur enabled guard lagaya —
//         taaki login se pehle poll na ho, aur alag account ka
//         unread-count cache mix na ho.
// Polls /notifications/unread-count every 30 seconds
// ============================================================

import { useQuery } from '@tanstack/react-query'
import { getUnreadCount } from '../api/notificationsApi'
import { useAuthStore } from '../store/authStore'

export function useUnreadCount() {
  const userId = useAuthStore(s => s.userId)
  const { data } = useQuery({
    queryKey:  ['notifications', 'unread-count', userId],
    queryFn:   () => getUnreadCount().then(r => r.data),
    enabled:   !!userId,
    // Refetch every 30 seconds so badge stays fresh
    refetchInterval: 30_000,
    // Also refetch when tab becomes active again
    refetchOnWindowFocus: true,
  })

  return {
    unreadCount: data?.unread_count ?? 0,
    hasUnread:   data?.has_unread ?? false,
  }
}