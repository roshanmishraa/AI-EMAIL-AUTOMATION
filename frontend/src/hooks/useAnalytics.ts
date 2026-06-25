import { useQuery } from '@tanstack/react-query'
import { getDashboard } from '../api/analyticsApi'
export const useAnalytics = () => useQuery({ queryKey: ['dashboard'], queryFn: getDashboard })
