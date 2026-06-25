import { NavLink } from 'react-router-dom'
import { Mail, BarChart2, BookOpen, Settings } from 'lucide-react'

const links = [
  { to: '/inbox',     icon: Mail,      label: 'Inbox'     },
  { to: '/analytics', icon: BarChart2, label: 'Analytics' },
  { to: '/kb',        icon: BookOpen,  label: 'Knowledge Base' },
  { to: '/settings',  icon: Settings,  label: 'Settings'  },
]

export default function Sidebar() {
  return (
    <aside className="w-56 border-r bg-white flex flex-col py-6 px-3 gap-1">
      <div className="px-3 pb-4 text-sm font-semibold text-gray-400 uppercase tracking-wider">AI Email</div>
      {links.map(({ to, icon: Icon, label }) => (
        <NavLink
          key={to} to={to}
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
              isActive ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'
            }`
          }
        >
          <Icon size={16} /> {label}
        </NavLink>
      ))}
    </aside>
  )
}
