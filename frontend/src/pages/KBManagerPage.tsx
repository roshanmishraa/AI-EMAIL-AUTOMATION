import { useState } from 'react'
import { useKBDocs, useUploadKBDoc, useDeleteKBDoc } from '../hooks/useKB'
import Topbar from '../components/layout/Topbar'
import ArticleList from '../components/kb/ArticleList'
import UploadModal from '../components/kb/UploadModal'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { Upload } from 'lucide-react'

export default function KBManagerPage() {
  const [showUpload, setShowUpload] = useState(false)
  const { data, isLoading, isError } = useKBDocs()
  const uploadMutation = useUploadKBDoc()
  const deleteMutation = useDeleteKBDoc()

  const docs = data?.documents ?? []

  const handleUpload = async (form: FormData) => {
    await uploadMutation.mutateAsync(form)
    setShowUpload(false)
  }

  return (
    <div className="flex flex-col h-full">
      <Topbar
        title="Knowledge Base"
        subtitle={`${docs.length} article${docs.length !== 1 ? 's' : ''} indexed`}
        actions={
          <button
            onClick={() => setShowUpload(true)}
            className="flex items-center gap-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded-lg transition-colors"
          >
            <Upload size={14} /> Upload Article
          </button>
        }
      />

      <div className="flex-1 overflow-auto p-6">
        {isLoading && (
          <div className="flex items-center justify-center h-48">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {isError && (
          <div className="px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            Failed to load KB documents — check backend connection.
          </div>
        )}

        {!isLoading && !isError && (
          <ArticleList
            docs={docs}
            onDelete={id => deleteMutation.mutate(id)}
            isDeleting={deleteMutation.isPending}
          />
        )}
      </div>

      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onUpload={handleUpload}
          isUploading={uploadMutation.isPending}
          error={uploadMutation.isError ? 'Upload failed — try again.' : null}
        />
      )}
    </div>
  )
}
