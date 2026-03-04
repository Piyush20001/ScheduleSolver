import { Users, CalendarClock, AlertTriangle, Clock } from 'lucide-react'
import { Card } from '../ui/Card'
import { SkeletonCard } from '../ui/Skeleton'
import { useEmployees, useShifts, useIncidents, useCoverageStats } from '../../hooks/api'

function formatResolutionTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.round(seconds % 60)
  if (mins === 0) return `${secs}s`
  return `${mins}m ${secs}s`
}

interface StatCardProps {
  label: string
  value: string | number
  icon: React.ReactNode
  colorClass: string
}

function StatCard({ label, value, icon, colorClass }: StatCardProps) {
  return (
    <Card className="relative overflow-hidden">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-400">{label}</p>
          <p className="text-3xl font-bold text-white mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-xl ${colorClass}`}>
          {icon}
        </div>
      </div>
    </Card>
  )
}

export function StatCards() {
  const today = new Date().toISOString().split('T')[0]

  const employeesQuery = useEmployees()
  const shiftsQuery = useShifts({ start_date: today, end_date: today })
  const incidentsQuery = useIncidents()
  const coverageQuery = useCoverageStats()

  const isLoading =
    employeesQuery.isLoading ||
    shiftsQuery.isLoading ||
    incidentsQuery.isLoading ||
    coverageQuery.isLoading

  if (isLoading) {
    return (
      <div className="grid grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    )
  }

  const totalEmployees = employeesQuery.data?.length ?? '---'
  const openShiftsToday = shiftsQuery.data?.filter((s) => s.status === 'open').length ?? '---'
  const activeIncidents =
    incidentsQuery.data?.filter(
      (i) => i.status === 'open' || i.status === 'in_progress'
    ).length ?? '---'
  const avgResolutionTime = coverageQuery.data
    ? formatResolutionTime(coverageQuery.data.avg_time_to_cover_seconds)
    : '---'

  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard
        label="Total Employees"
        value={totalEmployees}
        icon={<Users className="w-6 h-6 text-cyan-400" />}
        colorClass="bg-cyan-500/10"
      />
      <StatCard
        label="Open Shifts Today"
        value={openShiftsToday}
        icon={<CalendarClock className="w-6 h-6 text-amber-400" />}
        colorClass="bg-amber-500/10"
      />
      <StatCard
        label="Active Incidents"
        value={activeIncidents}
        icon={<AlertTriangle className="w-6 h-6 text-rose-400" />}
        colorClass="bg-rose-500/10"
      />
      <StatCard
        label="Avg Resolution Time"
        value={avgResolutionTime}
        icon={<Clock className="w-6 h-6 text-emerald-400" />}
        colorClass="bg-emerald-500/10"
      />
    </div>
  )
}
