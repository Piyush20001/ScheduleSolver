import { Activity } from 'lucide-react'
import { Card } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { SkeletonLine } from '../ui/Skeleton'
import { EmptyState } from '../ui/EmptyState'
import { useIncidents } from '../../hooks/api'

function timeAgo(dateString: string): string {
  const now = Date.now()
  const then = new Date(dateString).getTime()
  const diffSeconds = Math.floor((now - then) / 1000)

  if (diffSeconds < 60) return `${diffSeconds}s ago`
  const diffMinutes = Math.floor(diffSeconds / 60)
  if (diffMinutes < 60) return `${diffMinutes}m ago`
  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}

function getStatusVariant(status: string): 'warning' | 'info' | 'success' | 'danger' {
  switch (status) {
    case 'open':
      return 'warning'
    case 'in_progress':
      return 'info'
    case 'resolved':
      return 'success'
    case 'escalated':
      return 'danger'
    default:
      return 'warning'
  }
}

function getStatusDotColor(status: string): string {
  switch (status) {
    case 'open':
      return 'bg-amber-400'
    case 'in_progress':
      return 'bg-cyan-400'
    case 'resolved':
      return 'bg-emerald-400'
    case 'escalated':
      return 'bg-rose-400'
    default:
      return 'bg-slate-400'
  }
}

export function ActivityFeed() {
  const { data: incidents, isLoading } = useIncidents()

  const recentIncidents = incidents
    ? [...incidents]
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .slice(0, 5)
    : []

  return (
    <Card>
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5 text-cyan-400" />
        <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
          Recent Activity
        </h3>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <SkeletonLine key={i} height="h-12" />
          ))}
        </div>
      )}

      {!isLoading && recentIncidents.length === 0 && (
        <EmptyState title="No incidents recorded" />
      )}

      {!isLoading && recentIncidents.length > 0 && (
        <div>
          {recentIncidents.map((incident) => (
            <div
              key={incident.id}
              className="flex items-center gap-3 py-3 border-b border-slate-700/50 last:border-0"
            >
              <div className={`w-2 h-2 rounded-full ${getStatusDotColor(incident.status)}`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white truncate">
                  {incident.incident_id} &mdash; {incident.original_employee_name}
                </p>
                <p className="text-xs text-slate-400">
                  {incident.role_required ?? 'Unknown'} &middot; {timeAgo(incident.created_at)}
                </p>
              </div>
              <Badge variant={getStatusVariant(incident.status)}>{incident.status}</Badge>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
