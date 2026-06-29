import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useKBDocs, useUploadKBDoc, useDeleteKBDoc } from '../hooks/useKB';
import Topbar from '../components/layout/Topbar';
import ArticleList from '../components/kb/ArticleList';
import UploadModal from '../components/kb/UploadModal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Upload } from 'lucide-react';
export default function KBManagerPage() {
    const [showUpload, setShowUpload] = useState(false);
    const { data, isLoading, isError } = useKBDocs();
    const uploadMutation = useUploadKBDoc();
    const deleteMutation = useDeleteKBDoc();
    const docs = data?.documents ?? [];
    const handleUpload = async (form) => {
        await uploadMutation.mutateAsync(form);
        setShowUpload(false);
    };
    return (_jsxs("div", { className: "flex flex-col h-full", children: [_jsx(Topbar, { title: "Knowledge Base", subtitle: `${docs.length} article${docs.length !== 1 ? 's' : ''} indexed`, actions: _jsxs("button", { onClick: () => setShowUpload(true), className: "flex items-center gap-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded-lg transition-colors", children: [_jsx(Upload, { size: 14 }), " Upload Article"] }) }), _jsxs("div", { className: "flex-1 overflow-auto p-6", children: [isLoading && (_jsx("div", { className: "flex items-center justify-center h-48", children: _jsx(LoadingSpinner, { size: "lg" }) })), isError && (_jsx("div", { className: "px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700", children: "Failed to load KB documents \u2014 check backend connection." })), !isLoading && !isError && (_jsx(ArticleList, { docs: docs, onDelete: id => deleteMutation.mutate(id), isDeleting: deleteMutation.isPending }))] }), showUpload && (_jsx(UploadModal, { onClose: () => setShowUpload(false), onUpload: handleUpload, isUploading: uploadMutation.isPending, error: uploadMutation.isError ? 'Upload failed — try again.' : null }))] }));
}
