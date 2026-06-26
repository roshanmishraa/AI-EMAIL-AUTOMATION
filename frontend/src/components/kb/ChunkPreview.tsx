import { BookOpen } from 'lucide-react'

interface Props {
  chunks: string[]
}

export default function ChunkPreview({ chunks }: Props) {
  if (!chunks || chunks.length === 0) {
    return (
      <div className="text-xs text-gray-400 italic">No chunks to preview.</div>
    )
  }

  return (
    <div className="space-y-2 max-h-64 overflow-y-auto">
      {chunks.map((chunk, i) => (
        <div
          key={i}
          className="bg-gray-50 border border-gray-100 rounded-lg px-3 py-2"
        >
          <div className="flex items-center gap-1.5 mb-1">
            <BookOpen size={10} className="text-gray-400" />
            <span className="text-[10px] text-gray-400 font-medium uppercase tracking-wide">
              Chunk {i + 1}
            </span>
          </div>

          <p className="text-xs text-gray-600 leading-relaxed line-clamp-3">
            {chunk}
          </p>
        </div>
      ))}
    </div>
  )
}
