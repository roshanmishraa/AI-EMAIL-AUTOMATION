import { NavLink } from 'react-router-dom'
import { Mail, BarChart2, BookOpen, Settings, Zap } from 'lucide-react'

const links = [
  { to: '/inbox',     icon: Mail,      label: 'Inbox'          },
  { to: '/analytics', icon: BarChart2, label: 'Analytics'      },
  { to: '/kb',        icon: BookOpen,  label: 'Knowledge Base' },
  { to: '/settings',  icon: Settings,  label: 'Settings'       },
]

export default function Sidebar() {
  return (
    <aside className="w-60 border-r bg-white flex flex-col py-6 px-3 gap-1 shrink-0">
      <div className="px-3 pb-5 flex items-center gap-2">
        <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center">
          <Zap size={14} className="text-white" />
        </div>
        <div>
          <div className="text-sm font-bold text-gray-900">AI Email</div>
          <div className="text-xs text-gray-400">Automation</div>
        </div>
      </div>

      <div className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest px-3 pb-1">
        Navigation
      </div>

      {links.map(({ to, icon: Icon, label }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              isActive
                ? 'bg-blue-50 text-blue-700 font-medium'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`
          }
        >
          <Icon size={16} />
          {label}
        </NavLink>
      ))}

      <div className="mt-auto px-3 pt-4 border-t">
        <div className="text-xs text-gray-400">
          Backend: <span className="text-green-500 font-medium">localhost:8000</span>
        </div>
        <div className="text-xs text-gray-400 mt-0.5">
          CORS: <span className="text-green-500 font-medium">✓ allowed</span>
        </div>
      </div>
    </aside>
  )
}