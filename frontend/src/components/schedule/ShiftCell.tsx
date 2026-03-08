import { Badge } from '../ui/Badge'
import type { ShiftEnriched } from '../../types'

interface ShiftCellProps {
  shift: ShiftEnriched | null
  onClick?: () => void
}

const STATUS_STYLES: Record<string, { bg: string; border: string; text: string }> = {
  scheduled: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    text: 'text-blue-400',
  },
  open: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    text: 'text-amber-400',
  },
  covered: {
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    text: 'text-emerald-400',
  },
  cancelled: {
    bg: 'bg-slate-600/10',
    border: 'border-slate-600/30',
    text: 'text-slate-500',
  },
}

function getStatusBadgeVariant(status: string): 'info' | 'warning' | 'success' | 'default' {
  switch (status) {
    case 'scheduled':
      return 'info'
    case 'open':
      return 'warning'
    case 'covered':
      return 'success'
    default:
      return 'default'
  }
}

export function ShiftCell({ shift, onClick }: ShiftCellProps) {
  if (!shift) {
    return (
      <div className="min-h-[80px] p-2 rounded-lg border border-dashed border-slate-700/50 flex items-center justify-center">
        <span className="text-xs text-slate-600">No shift</span>
      </div>
    )
  }

  const style = STATUS_STYLES[shift.status] ?? STATUS_STYLES.cancelled
  const isClickable = shift.status === 'open' && !!onClick

  return (
    <div
      className={`min-h-[80px] p-2 rounded-lg border ${style.bg} ${style.border} ${
        isClickable
          ? 'cursor-pointer hover:border-amber-400 transition-colors'
          : ''
      } relative`}
      onClick={isClickable ? onClick : undefined}
    >
      <div className="absolute top-1 right-1">
        <Badge variant={getStatusBadgeVariant(shift.status)} size="sm">
          {shift.status}
        </Badge>
      </div>
      <p className={`text-xs font-medium capitalize ${style.text} mt-0.5`}>
        {shift.role_required}
      </p>
      <p className="text-xs text-slate-300 mt-1 truncate">
        {shift.status === 'open'
          ? 'Open'
          : shift.assigned_employee_name ?? 'Unassigned'}
      </p>
      <p className="text-xs text-slate-500 mt-1">
        {shift.start_time} - {shift.end_time}
      </p>
    </div>
  )
}
