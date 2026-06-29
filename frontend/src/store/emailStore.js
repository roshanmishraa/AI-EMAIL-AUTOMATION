import { create } from 'zustand';
export const useEmailStore = create(set => ({
    filter: {},
    setFilter: f => set({ filter: f }),
    clearFilter: () => set({ filter: {} }),
}));
