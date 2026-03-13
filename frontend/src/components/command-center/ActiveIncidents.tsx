import { AlertCircle } from 'lucide-react'
import { Card } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { SkeletonCard } from '../ui/Skeleton'
import { EmptyState } from '../ui/EmptyState'
import { useIncidents } from '../../hooks/api'

interface ActiveIncidentsProps {
  activeIncidentId: string | null
}

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

function getUrgencyVariant(urgency: string): 'danger' | 'warning' | 'default' {
  switch (urgency) {
    case 'high':
      return 'danger'
    case 'medium':
      return 'warning'
    default:
      return 'default'
  }
}

function getStatusVariant(status: string): 'warning' | 'info' | 'danger' {
  switch (status) {
    case 'open':
      return 'warning'
    case 'in_progress':
      return 'info'
    case 'escalated':
      return 'danger'
    default:
      return 'warning'
  }
}

export function ActiveIncidents({ activeIncidentId }: ActiveIncidentsProps) {
  const { data: allIncidents, isLoading } = useIncidents()

  const activeIncidents = allIncidents?.filter(
    (i) => i.status === 'open' || i.status === 'in_progress'
  ) ?? []

  return (
    <Card>
      <div className="flex items-center gap-2 mb-4">
        <AlertCircle className="w-5 h-5 text-cyan-400" />
        <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
          Active Incidents
        </h3>
        {activeIncidents.length > 0 && (
          <Badge variant="info" size="sm">
            {activeIncidents.length}
          </Badge>
        )}
      </div>

      {isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      )}

      {!isLoading && activeIncidents.length === 0 && (
        <EmptyState title="No active incidents" />
      )}

      {!isLoading && activeIncidents.length > 0 && (
        <div className="space-y-2">
          {activeIncidents.map((incident) => (
            <div
              key={incident.id}
              className={`p-3 rounded-lg border transition-colors ${
                incident.incident_id === activeIncidentId
                  ? 'bg-cyan-500/10 border-cyan-500/30'
                  : 'bg-slate-800/50 border-slate-700/50'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-mono text-white">{incident.incident_id}</span>
                <Badge variant={getUrgencyVariant(incident.urgency)}>{incident.urgency}</Badge>
              </div>
              <p className="text-sm text-slate-300">{incident.original_employee_name}</p>
              <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                <span>{incident.shift_type}</span>
                <span>&middot;</span>
                <span>{incident.role_required}</span>
                <span>&middot;</span>
                <Badge size="sm" variant={getStatusVariant(incident.status)}>
                  {incident.status}
                </Badge>
              </div>
              <p className="text-xs text-slate-600 mt-1">{timeAgo(incident.created_at)}</p>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
