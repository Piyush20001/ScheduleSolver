import { BarChart3 } from 'lucide-react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'
import { Card } from '../ui/Card'
import { SkeletonCard } from '../ui/Skeleton'
import { useShifts } from '../../hooks/api'

function getDayLabel(dateString: string): string {
  const date = new Date(dateString + 'T00:00:00')
  return date.toLocaleDateString('en-US', { weekday: 'short' })
}

function getSevenDaysAgo(): string {
  const d = new Date()
  d.setDate(d.getDate() - 6)
  return d.toISOString().split('T')[0]
}

function getToday(): string {
  return new Date().toISOString().split('T')[0]
}

export function ShiftCoverageChart() {
  const startDate = getSevenDaysAgo()
  const endDate = getToday()
  const { data: shifts, isLoading } = useShifts({ start_date: startDate, end_date: endDate })

  if (isLoading) {
    return <SkeletonCard className="h-[280px]" />
  }

  const grouped: Record<string, { total: number; covered: number }> = {}

  if (shifts) {
    for (const shift of shifts) {
      if (!grouped[shift.date]) {
        grouped[shift.date] = { total: 0, covered: 0 }
      }
      grouped[shift.date].total += 1
      if (shift.status === 'scheduled' || shift.status === 'covered') {
        grouped[shift.date].covered += 1
      }
    }
  }

  const chartData = Object.entries(grouped)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, { total, covered }]) => ({
      day: getDayLabel(date),
      coverage: total > 0 ? Math.round((covered / total) * 100) : 0,
    }))

  return (
    <Card>
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-5 h-5 text-cyan-400" />
        <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
          Shift Coverage (Last 7 Days)
        </h3>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis
            dataKey="day"
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            axisLine={{ stroke: '#334155' }}
          />
          <YAxis
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            axisLine={{ stroke: '#334155' }}
            domain={[0, 100]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#e2e8f0' }}
            itemStyle={{ color: '#22d3ee' }}
          />
          <Bar
            dataKey="coverage"
            fill="#22d3ee"
            radius={[4, 4, 0, 0]}
            animationDuration={1000}
          />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}
