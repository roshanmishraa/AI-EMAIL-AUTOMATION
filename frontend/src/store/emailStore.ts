import { create } from 'zustand'
import { EmailFilterParams } from '../api/emailsApi'

interface EmailStore {
  filter: EmailFilterParams
  setFilter: (f: EmailFilterParams) => void
  clearFilter: () => void
}

export const useEmailStore = create<EmailStore>(set => ({
  filter: {},
  setFilter: f => set({ filter: f }),
  clearFilter: () => set({ filter: {} }),
}))