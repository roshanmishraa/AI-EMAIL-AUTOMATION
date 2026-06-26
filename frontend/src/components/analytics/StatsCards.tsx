import { Mail, CheckCircle, AlertTriangle, Zap } from 'lucide-react'
import { DashboardStats } from '../../types/analytics'

interface Props { stats: DashboardStats }

const cards = (s: DashboardStats) => [
  {
    label: 'Total Emails',
    value: s.total_emails,
    icon:  Mail,
    color: 'text-blue-600',
    bg:    'bg-blue-50',
  },
  {
    label: 'Auto Replied',
    value: s.replied,
    icon:  CheckCircle,
    color: 'text-green-600',
    bg:    'bg-green-50',
  },
  {
    label: 'Escalated',
    value: s.escalated,
    icon:  AlertTriangle,
    color: 'text-red-600',
    bg:    'bg-red-50',
  },
  {
    label: 'Avg Confidence',
    value: `${Math.round(s.avg_confidence)}%`,
    icon:  Zap,
    color: s.avg_confidence >= 80 ? 'text-green-600' : s.avg_confidence >= 60 ? 'text-yellow-600' : 'text-red-600',
    bg:    s.avg_confidence >= 80 ? 'bg-green-50'    : s.avg_confidence >= 60 ? 'bg-yellow-50'    : 'bg-red-50',
  },
]

export default function StatsCards({ stats }: Props) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards(stats).map(card => (
        <div key={card.label} className="bg-white border border-gray-100 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-gray-500">{card.label}</span>
            <div className={`w-8 h-8 rounded-lg ${card.bg} flex items-center justify-center`}>
              <card.icon size={16} className={card.color} />
            </div>
          </div>
          <div className={`text-2xl font-bold ${card.color}`}>{card.value}</div>
        </div>
      ))}
    </div>
  )
}
