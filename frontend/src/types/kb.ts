export interface KBDoc {
  id: number
  title: string        // backend returns "title" (filename)
  source_type: string  // "pdf" | "docx" | "txt"
  chunk_count: number  // backend returns "chunk_count"
  created_at: string
}

export interface KBListOut {
  total: number
  documents: KBDoc[]
}