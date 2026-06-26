import { useAnalytics } from '../hooks/useAnalytics'
import Topbar from '../components/layout/Topbar'
import StatsCards from '../components/analytics/StatsCards'
import CategoryPie from '../components/analytics/CategoryPie'
import SentimentChart from '../components/analytics/SentimentChart'
import LoadingSpinner from '../components/common/LoadingSpinner'

export default function AnalyticsPage() {
  const { data: stats, isLoading, isError } = useAnalytics()

  return (
    <div className="flex flex-col h-full">
      <Topbar title="Analytics" subtitle="Email pipeline overview" />

      <div className="flex-1 overflow-auto p-6 space-y-6">

        {isLoading && (
          <div className="flex items-center justify-center h-48">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {isError && (
          <div className="px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            Failed to load analytics — check backend connection.
          </div>
        )}

        {stats && (
          <>
            <StatsCards stats={stats} />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
                <h2 className="text-sm font-semibold text-gray-700 mb-4">
                  Category Breakdown
                </h2>
                <CategoryPie distribution={stats.category_distribution} />
              </div>

              <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
                <h2 className="text-sm font-semibold text-gray-700 mb-4">
                  Sentiment Distribution
                </h2>
                <SentimentChart distribution={stats.sentiment_distribution} />
              </div>
            </div>

            {/* Status breakdown table */}
            <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">
                Pipeline Status
              </h2>

              <div className="grid grid-cols-3 gap-4">
                {[
                  { label: 'Processed', value: stats.processed, color: 'text-purple-600', bg: 'bg-purple-50' },
                  { label: 'Replied', value: stats.replied, color: 'text-green-600', bg: 'bg-green-50' },
                  { label: 'Escalated', value: stats.escalated, color: 'text-red-600', bg: 'bg-red-50' },
                ].map(item => (
                  <div key={item.label} className={`rounded-xl p-4 ${item.bg}`}>
                    <p className="text-xs text-gray-500 mb-1">{item.label}</p>
                    <p className={`text-2xl font-bold ${item.color}`}>{item.value}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {stats.total_emails > 0
                        ? `${Math.round((item.value / stats.total_emails) * 100)}% of total`
                        : '—'}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}