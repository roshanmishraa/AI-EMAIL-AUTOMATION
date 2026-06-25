import { useQuery } from '@tanstack/react-query'
import { getKBDocs } from '../api/kbApi'
export const useKBDocs = () => useQuery({ queryKey: ['kb-docs'], queryFn: getKBDocs })
