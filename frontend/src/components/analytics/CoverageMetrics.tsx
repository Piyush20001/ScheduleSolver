import { Phone, CheckCircle, Timer } from 'lucide-react'
import { Card } from '../ui/Card'
import { SkeletonCard } from '../ui/Skeleton'
import type { CoverageStats } from '../../types'

interface CoverageMetricsProps {
  stats: CoverageStats | undefined
  isLoading: boolean
}

function formatSeconds(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.round(seconds % 60)
  if (mins === 0) return `${secs}s`
  return `${mins}m ${secs}s`
}

export function CoverageMetrics({ stats, isLoading }: CoverageMetricsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-3 gap-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-3 gap-4">
      <Card>
        <div className="flex items-center gap-2 mb-2">
          <Phone className="w-4 h-4 text-cyan-400" />
          <p className="text-xs text-slate-400 uppercase tracking-wider">
            Avg Calls to Resolution
          </p>
        </div>
        <p className="text-3xl font-bold text-white font-mono">
          {stats?.avg_calls_to_resolution.toFixed(1) ?? '---'}
        </p>
        <p className="text-xs text-slate-500 mt-1">calls per incident</p>
      </Card>

      <Card>
        <div className="flex items-center gap-2 mb-2">
          <CheckCircle className="w-4 h-4 text-emerald-400" />
          <p className="text-xs text-slate-400 uppercase tracking-wider">Resolution Rate</p>
        </div>
        <p className="text-3xl font-bold text-white font-mono">
          {stats?.resolution_rate_percent.toFixed(1) ?? '---'}%
        </p>
        <p className="text-xs text-slate-500 mt-1">of incidents resolved</p>
      </Card>

      <Card>
        <div className="flex items-center gap-2 mb-2">
          <Timer className="w-4 h-4 text-amber-400" />
          <p className="text-xs text-slate-400 uppercase tracking-wider">Avg Time to Cover</p>
        </div>
        <p className="text-3xl font-bold text-white font-mono">
          {stats ? formatSeconds(stats.avg_time_to_cover_seconds) : '---'}
        </p>
        <p className="text-xs text-slate-500 mt-1">average resolution time</p>
      </Card>
    </div>
  )
}
