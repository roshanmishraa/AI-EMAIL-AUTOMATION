import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface Props {
  distribution: Record<string, number>
}

const COLORS: Record<string, string> = {
  legal: '#ef4444',
  billing: '#eab308',
  product_issue: '#a855f7',
  delivery: '#6366f1',
  refund: '#ec4899',
  general: '#9ca3af',
  spam: '#64748b',
  feedback: '#14b8a6',
}

const ICONS: Record<string, string> = {
  legal: '⚖️',
  billing: '💳',
  product_issue: '🔧',
  delivery: '📦',
  refund: '↩️',
  general: '✉️',
  spam: '🚫',
  feedback: '⭐',
}

export default function CategoryPie({ distribution }: Props) {
  const data = Object.entries(distribution)
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({
      name: `${ICONS[name] ?? ''} ${name.replace('_', ' ')}`,
      key: name,
      value,
    }))

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
        No category data yet
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={55}
          outerRadius={90}
          paddingAngle={3}
          dataKey="value"
        >
          {data.map((entry) => (
            <Cell key={entry.key} fill={COLORS[entry.key] ?? '#9ca3af'} />
          ))}
        </Pie>

        <Tooltip
          formatter={(value: number, name: string) => [value, name]}
          contentStyle={{ fontSize: 12, borderRadius: 8 }}
        />

        <Legend
          iconType="circle"
          iconSize={8}
          wrapperStyle={{ fontSize: 11 }}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
