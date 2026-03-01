import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Sidebar } from './Sidebar'
import { useWebSocket } from '../../hooks/useWebSocket'

export function Layout() {
  const [collapsed, setCollapsed] = useState(false)
  const { status: wsStatus } = useWebSocket()

  return (
    <div className="min-h-screen bg-slate-950">
      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed((prev) => !prev)}
        wsConnected={wsStatus === 'connected'}
        wsStatus={wsStatus}
      />
      <motion.main
        animate={{ marginLeft: collapsed ? 64 : 256 }}
        transition={{ duration: 0.2, ease: 'easeInOut' }}
        className="p-6 min-h-screen"
      >
        <Outlet />
      </motion.main>
    </div>
  )
}
