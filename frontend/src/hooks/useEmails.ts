import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getEmails, getEmail, approveReply, escalateEmail, processEmail, triggerFetch, EmailFilterParams } from '../api/emailsApi'

export const useEmails = (params?: EmailFilterParams) =>
  useQuery({
    queryKey: ['emails', params],
    queryFn: () => getEmails(params),
    select: res => res.data,
    refetchInterval: 30000,
  })

export const useEmail = (id: number) =>
  useQuery({
    queryKey: ['email', id],
    queryFn: () => getEmail(id),
    select: res => res.data,
    enabled: !!id,
  })

export const useApproveReply = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => approveReply(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ['email', id] })
      qc.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

export const useEscalateEmail = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => escalateEmail(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ['email', id] })
      qc.invalidateQueries({ queryKey: ['emails'] })
    },
  })
}

export const useProcessEmail = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => processEmail(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ['email', id] })
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
