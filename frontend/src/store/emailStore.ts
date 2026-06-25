import { create } from 'zustand'
interface EmailStore { filter: object; setFilter: (f: object) => void }
export const useEmailStore = create<EmailStore>(set => ({ filter: {}, setFilter: f => set({ filter: f }) }))
