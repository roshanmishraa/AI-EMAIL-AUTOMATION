// ============================================================
// FILE:  frontend/src/hooks/useKB.ts
// CHANGE: userId ko queryKey mein add kiya — taaki alag account ke
//         KB documents ka cache mix na ho.
// ============================================================
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getKBDocs, uploadKBDoc, deleteKBDoc } from '../api/kbApi'
import { useAuthStore } from '../store/authStore'

export const useKBDocs = () => {
  const userId = useAuthStore(s => s.userId)
  return useQuery({
    queryKey: ['kb-docs', userId],
    queryFn: getKBDocs,
    select: res => res.data,
    enabled: !!userId,
  })
}

export const useUploadKBDoc = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (form: FormData) => uploadKBDoc(form),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['kb-docs'] }),
  })
}

export const useDeleteKBDoc = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => deleteKBDoc(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['kb-docs'] }),
  })
}