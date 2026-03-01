import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  Users,
  Calendar,
  Radio,
  BarChart3,
  Bot,
  ChevronLeft,
  ChevronRight,
  Wifi,
  WifiOff,
} from 'lucide-react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/employees', label: 'Employees', icon: Users },
  { path: '/schedule', label: 'Schedule', icon: Calendar },
  { path: '/command-center', label: 'Command Center', icon: Radio },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/agent', label: 'Agent', icon: Bot },
]

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
  wsConnected: boolean
  wsStatus: 'connecting' | 'connected' | 'disconnected' | 'reconnecting'
}

export function Sidebar({ collapsed, onToggle, wsConnected: _wsConnected, wsStatus }: SidebarProps) {
  const statusConfig = {
    connected: { color: 'bg-emerald-400', label: 'Connected', pulse: false },
    disconnected: { color: 'bg-rose-400', label: 'Disconnected', pulse: false },
    connecting: { color: 'bg-amber-400', label: 'Connecting...', pulse: false },
    reconnecting: { color: 'bg-amber-400', label: 'Reconnecting...', pulse: true },
  }

  const status = statusConfig[wsStatus]

  return (
    <motion.aside
      animate={{ width: collapsed ? 64 : 256 }}
      transition={{ duration: 0.2, ease: 'easeInOut' }}
      className="bg-slate-900 border-r border-slate-700/50 min-h-screen fixed left-0 top-0 z-30 flex flex-col"
    >
      {/* Branding */}
      <div className="flex items-center gap-3 px-3 py-4 border-b border-slate-700/50">
        <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center">
          <Calendar className="w-5 h-5 text-white" />
        </div>
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="text-sm font-bold text-white whitespace-nowrap">ScheduleSolver</div>
            <div className="text-xs text-slate-400 whitespace-nowrap">ML Scheduling</div>
          </motion.div>
        )}
        <button
          onClick={onToggle}
          className="ml-auto flex-shrink-0 p-1.5 rounded-md text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 space-y-1 px-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-500/20 to-teal-500/20 text-white border-l-2 border-cyan-400'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              } ${collapsed ? 'justify-center px-0' : ''}`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-cyan-400' : ''}`} />
                {!collapsed && (
                  <span className="text-sm font-medium whitespace-nowrap">{item.label}</span>
                )}
                {!collapsed && isActive && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-cyan-400" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-3 py-3 border-t border-slate-700/50 space-y-2">
        {/* WebSocket Status */}
        <div className={`flex items-center gap-2 ${collapsed ? 'justify-center' : ''}`}>
          <div className="relative flex-shrink-0">
            <div className={`w-2 h-2 rounded-full ${status.color} ${status.pulse ? 'animate-pulse' : ''}`} />
          </div>
          {!collapsed && (
            <span className="text-xs text-slate-400">{status.label}</span>
          )}
          {!collapsed && (
            wsStatus === 'connected'
              ? <Wifi className="ml-auto w-3.5 h-3.5 text-slate-500" />
              : <WifiOff className="ml-auto w-3.5 h-3.5 text-slate-500" />
          )}
        </div>

        {/* ML Model Badge */}
        <div className={`flex items-center gap-2 ${collapsed ? 'justify-center' : ''}`}>
          <div className="w-2 h-2 rounded-full bg-slate-600 flex-shrink-0" />
          {!collapsed && (
            <span className="text-xs text-slate-500 font-mono">AUC: --</span>
          )}
        </div>
      </div>
    </motion.aside>
  )
}
