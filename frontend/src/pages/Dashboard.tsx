import { LayoutDashboard } from 'lucide-react'
import { StatCards } from '../components/dashboard/StatCards'
import { ActivityFeed } from '../components/dashboard/ActivityFeed'
import { ShiftCoverageChart } from '../components/dashboard/ShiftCoverageChart'
import { RoleDistributionChart } from '../components/dashboard/RoleDistributionChart'

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <LayoutDashboard className="w-6 h-6 text-cyan-400" />
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Overview of scheduling operations, active incidents, and key metrics
          </p>
        </div>
      </div>

      <StatCards />

      <div className="grid grid-cols-5 gap-4">
        <div className="col-span-3">
          <ActivityFeed />
        </div>
        <div className="col-span-2 space-y-4">
          <ShiftCoverageChart />
          <RoleDistributionChart />
        </div>
      </div>
    </div>
  )
}
