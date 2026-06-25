import { useEmailStore } from '../../store/emailStore'

const STATUS_OPTIONS = ['', 'new', 'processing', 'processed', 'replied', 'escalated']
const CATEGORY_OPTIONS = ['', 'legal', 'billing', 'product_issue', 'delivery', 'refund', 'general', 'spam', 'feedback']
const SENTIMENT_OPTIONS = ['', 'angry', 'frustrated', 'neutral', 'happy', 'sad']

export default function EmailFilters() {
  const { filter, setFilter, clearFilter } = useEmailStore()

  const hasFilter = filter.status || filter.category || filter.sentiment

  return (
    <div className="flex items-center gap-3 flex-wrap">
      <select
        value={filter.status ?? ''}
        onChange={e => setFilter({ ...filter, status: e.target.value || undefined })}
        className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">All Status</option>
        {STATUS_OPTIONS.filter(Boolean).map(s => (
          <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
        ))}
      </select>

      <select
        value={filter.category ?? ''}
        onChange={e => setFilter({ ...filter, category: e.target.value || undefined })}
        className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">All Categories</option>
        {CATEGORY_OPTIONS.filter(Boolean).map(c => (
          <option key={c} value={c}>{c.replace('_', ' ')}</option>
        ))}
      </select>

      <select
        value={filter.sentiment ?? ''}
        onChange={e => setFilter({ ...filter, sentiment: e.target.value || undefined })}
        className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">All Sentiments</option>
        {SENTIMENT_OPTIONS.filter(Boolean).map(s => (
          <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
        ))}
      </select>

      {hasFilter && (
        <button
          onClick={clearFilter}
          className="text-sm text-gray-400 hover:text-gray-600 underline"
        >
          Clear
        </button>
      )}
    </div>
  )
}
