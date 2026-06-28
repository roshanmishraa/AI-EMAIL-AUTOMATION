// ============================================================
// FILE:  frontend/src/api/kbApi.ts
// CHANGE: fetchChunksForEmail() function add kiya
// ============================================================

import client from './axiosClient'

export const getKBDocs = () => client.get('/kb/')

export const uploadKBDoc = (form: FormData) =>
  client.post('/kb/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

export const deleteKBDoc = (id: number) => client.delete(`/kb/${id}`)

// ── NEW: Fetch which KB chunks would be used for a given email ──
export interface ChunkPreviewResponse {
  email_id:      number
  email_subject: string
  category:      string | null
  chunks_found:  number
  chunks:        string[]
}

export const fetchChunksForEmail = (emailId: number) =>
  client.get<ChunkPreviewResponse>(`/kb/preview?email_id=${emailId}`)