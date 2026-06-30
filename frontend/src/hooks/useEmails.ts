// ============================================================
// FILE:  frontend/src/hooks/useEmails.ts
// CHANGE: userId ko queryKey mein add kiya — taaki alag account ka
//         cache mix na ho. invalidateQueries calls ko broader
//         ['email'] prefix se invalidate karne layak banaya kyunki
//         ab key shape ['email', userId, id] hai — ['email', id]
//         se match nahi hoga.
// ============================================================
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getEmails, getEmail, approveReply, escalateEmail,
  resolveEscalation, processEmail, triggerFetch, EmailFilterParams,
} from '../api/emailsApi'
import { useAuthStore } from '../store/authStore'

export const useEmails = (params?: EmailFilterParams) => {
  const userId = useAuthStore(s => s.userId)
  return useQuery({
    // NEW: userId queryKey mein — alag account ka cache mix nahi hoga
    queryKey: ['emails', userId, params],
    queryFn: () => getEmails(params),
    select: res => res.data,
    refetchInterval: 30000,
    enabled: !!userId,
  })
}

export const useEmail = (id: number) => {
  const userId = useAuthStore(s => s.userId)
  return useQuery({
    queryKey: ['email', userId, id],
    queryFn: () => getEmail(id),
    select: res => res.data,
    enabled: !!id && !!userId,
  })
}

export const useApproveReply = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => approveReply(id),
    onSuccess: () => {
      // NOTE: queryKey ab ['email', userId, id] hai — sirf ['email']
      // prefix se invalidate karo taaki userId/id chahe kuch bhi ho, match ho jaye
      qc.invalidateQueries({ queryKey: ['email'] })
      qc.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

export const useEscalateEmail = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => escalateEmail(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['email'] })
      qc.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

// NEW: escalation resolve karne ka hook
export const useResolveEscalation = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, notes }: { id: number; notes?: string }) => resolveEscalation(id, notes),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['email'] })
      qc.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

export const useProcessEmail = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => processEmail(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['email'] })
    },
  })
}

export const useTriggerFetch = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => triggerFetch(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}
