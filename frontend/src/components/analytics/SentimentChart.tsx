import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'

interface Props {
  distribution: Record<string, number>
}

const SENTIMENT_CONFIG: Record<string, { color: string; icon: string }> = {
  angry: { color: '#ef4444', icon: '😡' },
  frustrated: { color: '#f97316', icon: '😤' },
  neutral: { color: '#9ca3af', icon: '😐' },
  happy: { color: '#22c55e', icon: '😊' },
  sad: { color: '#60a5fa', icon: '😢' },
}

export default function SentimentChart({ distribution }: Props) {
  const data = Object.entries(distribution)
    .filter(([, v]) => v > 0)
    .map(([key, value]) => ({
      key,
      name: `${SENTIMENT_CONFIG[key]?.icon ?? ''} ${key}`,
      value,
      color: SENTIMENT_CONFIG[key]?.color ?? '#9ca3af',
    }))

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
        No sentiment data yet
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} barSize={36}>
        <XAxis
          dataKey="name"
          tick={{ fontSize: 11, fill: '#6b7280' }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          allowDecimals={false}
          tick={{ fontSize: 11, fill: '#9ca3af' }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          cursor={{ fill: '#f3f4f6' }}
          contentStyle={{ fontSize: 12, borderRadius: 8 }}
          formatter={(value: number) => [value, 'Emails']}
        />
        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
          {data.map((entry) => (
            <Cell key={entry.key} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
