// ============================================================
// FILE:  frontend/src/hooks/useSettings.ts
// CHANGE: userId ko queryKey mein add kiya — taaki alag account ka
//         settings cache mix na ho.
// ============================================================
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getSettings, updateSettings } from '../api/settingApi'
import { useAuthStore } from '../store/authStore'

export const useSettings = () => {
  const userId = useAuthStore(s => s.userId)
  return useQuery({
    queryKey: ['settings', userId],
    queryFn: getSettings,
    select: res => res.data,
    enabled: !!userId,
  })
}

export const useUpdateSettings = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: updateSettings,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['settings'] }),
  })
}