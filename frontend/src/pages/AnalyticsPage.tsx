import { useAnalytics } from '../hooks/useAnalytics'
import type { SentimentTrendPoint } from '../types/analytics'
import Topbar from '../components/layout/Topbar'
import StatsCards from '../components/analytics/StatsCards'
import CategoryPie from '../components/analytics/CategoryPie'
import SentimentChart from '../components/analytics/SentimentChart'
import LoadingSpinner from '../components/common/LoadingSpinner'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend
} from 'recharts'

// ── Escalation reason → human readable label ──
const REASON_LABELS: Record<string, string> = {
  legal:                'Legal',
  low_confidence:       'Low Confidence',
  angry_repeat:         'Angry Repeat',
  vip:                  'VIP Customer',
  sensitive_attachment: 'Sensitive Attachment',
}

// ── Sentiment → color for trend chart ──
const SENTIMENT_COLORS: Record<string, string> = {
  angry:      '#ef4444',
  frustrated: '#f97316',
  neutral:    '#6b7280',
  happy:      '#22c55e',
  sad:        '#3b82f6',
}

// ── Format seconds → "2m 30s" or "45s" ──
function formatResponseTime(seconds: number | null): string {
  if (seconds === null || seconds === undefined) return '—'
  if (seconds < 60) return `${Math.round(seconds)}s`
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  return s > 0 ? `${m}m ${s}s` : `${m}m`
}

export default function AnalyticsPage() {
  const { data: stats, isLoading, isError } = useAnalytics()

  // ── Build sentiment trend data for recharts ──
  const trendChartData: Record<string, string | number>[] = stats?.sentiment_trend.map((point: SentimentTrendPoint) => {
    const label = new Date(point.date).toLocaleDateString('en-IN', {
      month: 'short', day: 'numeric',
    })
    return { date: label, ...point.sentiment_counts }
  }) ?? []

  // ── All unique sentiments across trend data (for Bar keys) ──
  const trendSentiments: string[] = Array.from(
    new Set(
      trendChartData.flatMap(d => Object.keys(d).filter(k => k !== 'date'))
    )
  )

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

            {/* ── Row 1: Category + Sentiment ── */}
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

            {/* ── Row 2: Pipeline Status ── */}
            <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">
                Pipeline Status
              </h2>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { label: 'Processed', value: stats.processed,  color: 'text-purple-600', bg: 'bg-purple-50' },
                  { label: 'Replied',   value: stats.replied,    color: 'text-green-600',  bg: 'bg-green-50'  },
                  { label: 'Escalated', value: stats.escalated,  color: 'text-red-600',    bg: 'bg-red-50'    },
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

            {/* ── Row 3: Avg Response Time + Top Escalation Reasons ── */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

              {/* Avg Response Time */}
              <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
                <h2 className="text-sm font-semibold text-gray-700 mb-4">
                  Avg Response Time
                </h2>
                <div className="flex flex-col items-center justify-center h-32 gap-1">
                  <p className="text-4xl font-bold text-indigo-600">
                    {formatResponseTime(stats.avg_response_time_seconds)}
                  </p>
                  <p className="text-xs text-gray-400">
                    from email received → AI reply generated
                  </p>
                  {stats.avg_response_time_seconds === null && (
                    <p className="text-xs text-gray-400 italic mt-1">
                      No replies sent yet
                    </p>
                  )}
                </div>
              </div>

              {/* Top Escalation Reasons */}
              <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
                <h2 className="text-sm font-semibold text-gray-700 mb-4">
                  Top Escalation Reasons
                </h2>

                {Object.keys(stats.escalation_reasons).length === 0 ? (
                  <p className="text-sm text-gray-400 italic">No escalations yet.</p>
                ) : (
                  <div className="space-y-2">
                    {(Object.entries(stats.escalation_reasons) as [string, number][])
                      .sort(([, a], [, b]) => b - a)
                      .map(([reason, count]) => {
                        const pct = stats.escalated > 0
                          ? Math.round((count / stats.escalated) * 100)
                          : 0
                        return (
                          <div key={reason}>
                            <div className="flex justify-between text-xs text-gray-600 mb-0.5">
                              <span>{REASON_LABELS[reason] ?? reason}</span>
                              <span className="font-semibold">{count}</span>
                            </div>
                            <div className="w-full bg-gray-100 rounded-full h-1.5">
                              <div
                                className="bg-red-400 h-1.5 rounded-full transition-all"
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                          </div>
                        )
                      })}
                  </div>
                )}
              </div>
            </div>

            {/* ── Row 4: Sentiment Trend (last 7 days) ── */}
            <div className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
              <h2 className="text-sm font-semibold text-gray-700 mb-4">
                Sentiment Trend — Last 7 Days
              </h2>

              {trendChartData.length === 0 || trendSentiments.length === 0 ? (
                <p className="text-sm text-gray-400 italic">
                  Not enough data yet.
                </p>
              ) : (
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={trendChartData} barCategoryGap="30%">
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      allowDecimals={false}
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' }}
                    />
                    <Legend
                      wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
                      formatter={(val: string) =>
                        val.charAt(0).toUpperCase() + val.slice(1)
                      }
                    />
                    {trendSentiments.map((sentiment: string) => (
                      <Bar
                        key={sentiment}
                        dataKey={sentiment}
                        stackId="sentiment"
                        fill={SENTIMENT_COLORS[sentiment] ?? '#94a3b8'}
                        radius={
                          (sentiment === trendSentiments[trendSentiments.length - 1]
                            ? [4, 4, 0, 0]
                            : [0, 0, 0, 0]
                          ) as any
                        }
                      />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}