// ============================================================
// FILE:  frontend/src/api/notificationsApi.ts
// NEW FILE — create karo is path pe
// ============================================================

import client from './axiosClient'

export const getUnreadCount = () =>
  client.get<{ unread_count: number; has_unread: boolean }>('/notifications/unread-count')