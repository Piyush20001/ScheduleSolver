import { PieChart as PieChartIcon } from 'lucide-react'
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts'
import { Card } from '../ui/Card'
import { SkeletonCard } from '../ui/Skeleton'
import { useEmployees } from '../../hooks/api'

const ROLE_COLORS: Record<string, string> = {
  cook: '#22d3ee',
  server: '#2dd4bf',
  cashier: '#fbbf24',
  host: '#a78bfa',
  manager: '#fb7185',
  barista: '#34d399',
}

export function RoleDistributionChart() {
  const { data: employees, isLoading } = useEmployees()

  if (isLoading) {
    return <SkeletonCard className="h-[280px]" />
  }

  const roleCounts: Record<string, number> = {}
  if (employees) {
    for (const emp of employees) {
      const role = emp.role.toLowerCase()
      roleCounts[role] = (roleCounts[role] || 0) + 1
    }
  }

  const chartData = Object.entries(roleCounts).map(([name, value]) => ({
    name,
    value,
  }))

  return (
    <Card>
      <div className="flex items-center gap-2 mb-4">
        <PieChartIcon className="w-5 h-5 text-cyan-400" />
        <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
          Role Distribution
        </h3>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            paddingAngle={2}
            dataKey="value"
            animationDuration={1000}
          >
            {chartData.map((entry) => (
              <Cell
                key={entry.name}
                fill={ROLE_COLORS[entry.name] || '#64748b'}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#e2e8f0' }}
          />
          <Legend
            formatter={(value: string) => (
              <span className="text-slate-300 text-sm capitalize">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}
