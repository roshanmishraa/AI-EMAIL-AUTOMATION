// ============================================================
// FILE:  frontend/src/hooks/useNotifications.ts
// NEW FILE — create karo is path pe
// Polls /notifications/unread-count every 30 seconds
// ============================================================
import { useQuery } from '@tanstack/react-query';
import { getUnreadCount } from '../api/notificationsApi';
export function useUnreadCount() {
    const { data } = useQuery({
        queryKey: ['notifications', 'unread-count'],
        queryFn: () => getUnreadCount().then(r => r.data),
        // Refetch every 30 seconds so badge stays fresh
        refetchInterval: 30000,
        // Also refetch when tab becomes active again
        refetchOnWindowFocus: true,
    });
    return {
        unreadCount: data?.unread_count ?? 0,
        hasUnread: data?.has_unread ?? false,
    };
}
