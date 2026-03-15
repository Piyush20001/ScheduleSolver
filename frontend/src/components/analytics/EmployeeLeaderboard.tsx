import { Trophy } from 'lucide-react'
import { Card } from '../ui/Card'
import { SkeletonLine } from '../ui/Skeleton'
import { EmptyState } from '../ui/EmptyState'
import { ScoreBar } from '../common/ScoreBar'
import type { EmployeePerformance } from '../../types'

interface EmployeeLeaderboardProps {
  employees: EmployeePerformance[] | undefined
  isLoading: boolean
}

function getRankStyle(index: number): string {
  switch (index) {
    case 0:
      return 'bg-amber-500/20 text-amber-400'
    case 1:
      return 'bg-slate-400/20 text-slate-300'
    case 2:
      return 'bg-amber-700/20 text-amber-600'
    default:
      return 'bg-slate-700/50 text-slate-500'
  }
}

export function EmployeeLeaderboard({ employees, isLoading }: EmployeeLeaderboardProps) {
  const top5 = employees?.slice(0, 5) ?? []

  return (
    <Card>
      <div className="flex items-center gap-2 mb-4">
        <Trophy className="w-5 h-5 text-amber-400" />
        <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
          Top Performers
        </h3>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <SkeletonLine key={i} height="h-10" />
          ))}
        </div>
      )}

      {!isLoading && top5.length === 0 && (
        <EmptyState title="No call data yet" />
      )}

      {!isLoading && top5.length > 0 && (
        <div className="space-y-3">
          {top5.map((emp, index) => (
            <div key={emp.employee_id} className="flex items-center gap-3">
              {/* Rank badge */}
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${getRankStyle(index)}`}
              >
                {index + 1}
              </div>

              {/* Name and role */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{emp.name}</p>
                <p className="text-xs text-slate-400 capitalize">{emp.role}</p>
              </div>

              {/* Acceptance rate bar */}
              <div className="w-32">
                <ScoreBar score={emp.acceptance_rate} height="h-2" />
              </div>

              <span className="text-sm font-mono text-white w-14 text-right">
                {(emp.acceptance_rate * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
