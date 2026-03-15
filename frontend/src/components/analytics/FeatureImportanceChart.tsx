import { Layers } from 'lucide-react'
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

interface FeatureImportanceChartProps {
  featureImportances: Record<string, number> | undefined
  isLoading: boolean
}

function formatFeatureName(name: string): string {
  return name
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

export function FeatureImportanceChart({
  featureImportances,
  isLoading,
}: FeatureImportanceChartProps) {
  if (isLoading) {
    return <SkeletonCard className="h-[320px]" />
  }

  const chartData = Object.entries(featureImportances ?? {})
    .map(([name, value]) => ({
      name: formatFeatureName(name),
      value: Math.round(value * 1000) / 10,
    }))
    .sort((a, b) => b.value - a.value)

  const chartHeight = chartData.length * 40 + 40

  return (
    <Card>
      <div className="flex items-center gap-2 mb-4">
        <Layers className="w-5 h-5 text-cyan-400" />
        <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
          Feature Importance
        </h3>
      </div>
      <ResponsiveContainer width="100%" height={chartHeight}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ left: 120, right: 20, top: 10, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            axisLine={{ stroke: '#334155' }}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fill: '#e2e8f0', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            width={110}
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
            dataKey="value"
            fill="#22d3ee"
            radius={[0, 4, 4, 0]}
            animationDuration={1000}
          />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}
