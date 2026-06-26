import { useState, useRef } from 'react'
import { X, Upload, FileText } from 'lucide-react'
import LoadingSpinner from '../common/LoadingSpinner'

interface Props {
  onClose: () => void
  onUpload: (form: FormData) => Promise<void>
  isUploading: boolean
  error: string | null
}

const CATEGORY_OPTIONS = [
  { value: '', label: 'No category (matches all)' },
  { value: 'legal', label: '⚖️  Legal' },
  { value: 'billing', label: '💳  Billing' },
  { value: 'product_issue', label: '🔧  Product Issue' },
  { value: 'delivery', label: '📦  Delivery' },
  { value: 'refund', label: '↩️  Refund' },
  { value: 'general', label: '✉️  General' },
  { value: 'feedback', label: '⭐  Feedback' },
]

export default function UploadModal({
  onClose,
  onUpload,
  isUploading,
  error,
}: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [categoryTag, setCategoryTag] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async () => {
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    if (categoryTag) form.append('category_tag', categoryTag)
    await onUpload(form)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const dropped = e.dataTransfer.files[0]
    if (dropped) setFile(dropped)
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-base font-semibold text-gray-900">
            Upload KB Article
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 p-1 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        <div className="p-6 space-y-4">

          {/* Drop zone */}
          <div
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
              file
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
            }`}
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt,.md"
              className="hidden"
              onChange={(e) =>
                e.target.files?.[0] && setFile(e.target.files[0])
              }
            />

            {file ? (
              <div className="flex items-center justify-center gap-2 text-blue-700">
                <FileText size={18} />
                <span className="text-sm font-medium">{file.name}</span>
              </div>
            ) : (
              <>
                <Upload size={24} className="text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">
                  Drag & drop or{' '}
                  <span className="text-blue-600 font-medium">browse</span>
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  PDF, DOCX, TXT, MD
                </p>
              </>
            )}
          </div>

          {/* Category tag */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1.5">
              Category Tag{' '}
              <span className="text-gray-400 font-normal">
                (optional — for precision RAG retrieval)
              </span>
            </label>

            <select
              value={categoryTag}
              onChange={(e) => setCategoryTag(e.target.value)}
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {CATEGORY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {error && (
            <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">
              {error}
            </p>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t">
          <button
            onClick={onClose}
            className="text-sm text-gray-600 hover:text-gray-900 border border-gray-200 px-4 py-2 rounded-lg transition-colors"
          >
            Cancel
          </button>

          <button
            onClick={handleSubmit}
            disabled={!file || isUploading}
            className="flex items-center gap-2 text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-60 px-4 py-2 rounded-lg transition-colors font-medium"
          >
            {isUploading ? (
              <>
                <LoadingSpinner size="sm" /> Uploading…
              </>
            ) : (
              <>
                <Upload size={14} /> Upload
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
