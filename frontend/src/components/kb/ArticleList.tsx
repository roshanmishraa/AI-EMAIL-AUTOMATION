import { Trash2, FileText,  } from 'lucide-react'
import { KBDoc } from '../../types/kb'
import { formatDistanceToNow } from '../../types/date'

interface Props {
  docs: KBDoc[]
  onDelete: (id: number) => void
  isDeleting: boolean
}

const ICON_MAP: Record<string, string> = {
  pdf: '📄',
  docx: '📝',
  txt: '📃',
  md: '📃',
}

export default function ArticleList({ docs, onDelete, isDeleting }: Props) {
  if (docs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <FileText size={40} className="text-gray-200 mb-3" />
        <p className="text-gray-500 font-medium">No KB articles yet</p>
        <p className="text-gray-400 text-sm mt-1">
          Upload PDF, DOCX, or TXT files to ground AI replies in your company knowledge.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {docs.map(doc => (
        <div
          key={doc.id}
          className="bg-white border border-gray-100 rounded-xl px-5 py-4 shadow-sm flex items-center gap-4"
        >
          {/* File type icon */}
          <div className="text-2xl w-8 text-center shrink-0">
            {ICON_MAP[doc.source_type?.toLowerCase() ?? ''] ?? '📄'}
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {doc.title}
            </p>

            <div className="flex items-center gap-3 mt-0.5">
              <span className="text-xs text-gray-400 uppercase tracking-wide">
                {doc.source_type}
              </span>
              <span className="text-xs text-gray-400">·</span>
              <span className="text-xs text-gray-500">
                {doc.chunk_count} chunks indexed
              </span>

              {doc.created_at && (
                <>
                  <span className="text-xs text-gray-400">·</span>
                  <span className="text-xs text-gray-400">
                    {formatDistanceToNow(doc.created_at)}
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Delete button */}
          <div className="shrink-0">
            <button
              onClick={() => onDelete(doc.id)}
              disabled={isDeleting}
              className="text-gray-400 hover:text-red-600 disabled:opacity-40 p-1.5 rounded-lg hover:bg-red-50 transition-colors"
              title="Delete article"
            >
              <Trash2 size={14} />
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
