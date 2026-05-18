import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  TrendingUp,
  Route,
  AlertTriangle,
  Link2,
  Play,
  MessageSquare,
} from 'lucide-react'

const links = [
  { to: '/overview', icon: LayoutDashboard, label: 'Overview' },
  { to: '/orders', icon: ShoppingCart, label: 'Orders' },
  { to: '/inventory', icon: Package, label: 'Inventory' },
  { to: '/forecast', icon: TrendingUp, label: 'Forecasting' },
  { to: '/routes', icon: Route, label: 'Routes' },
  { to: '/anomalies', icon: AlertTriangle, label: 'Anomalies' },
  { to: '/affinity', icon: Link2, label: 'Affinity' },
  { to: '/simulation', icon: Play, label: 'Simulation' },
]

interface SidebarProps {
  onToggleChat: () => void
  chatOpen: boolean
}

export default function Sidebar({ onToggleChat, chatOpen }: SidebarProps) {
  return (
    <aside className="w-64 bg-navy-800 border-r border-navy-700 flex flex-col h-screen fixed left-0 top-0 z-30">
      <div className="p-5 border-b border-navy-700">
        <h1 className="text-lg font-bold text-text-primary flex items-center gap-2">
          <Package className="h-6 w-6 text-accent-cyan" />
          DarkStore
        </h1>
        <p className="text-xs text-text-secondary mt-0.5">Analytics Platform</p>
      </div>

      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-accent-cyan/10 text-accent-cyan'
                  : 'text-text-secondary hover:text-text-primary hover:bg-navy-700/50'
              }`
            }
          >
            <Icon className="h-5 w-5 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t border-navy-700">
        <button
          onClick={onToggleChat}
          className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors w-full ${
            chatOpen
              ? 'bg-accent-violet/10 text-accent-violet'
              : 'text-text-secondary hover:text-text-primary hover:bg-navy-700/50'
          }`}
        >
          <MessageSquare className="h-5 w-5 shrink-0" />
          AI Chat
        </button>
      </div>
    </aside>
  )
}
