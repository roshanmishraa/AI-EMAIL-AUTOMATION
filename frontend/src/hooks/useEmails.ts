import { useQuery } from '@tanstack/react-query'
import { getEmails } from '../api/emailsApi'
export const useEmails = (params?: object) => useQuery({ queryKey: ['emails', params], queryFn: () => getEmails(params) })
