import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '../ui/Button'

interface WeekNavigationProps {
  weekStart: Date
  onPrevWeek: () => void
  onNextWeek: () => void
  onCurrentWeek: () => void
}

export function getWeekStart(date: Date): Date {
  const d = new Date(date)
  const day = d.getDay()
  // Monday = 1, Sunday = 0. Adjust so Monday is start of week.
  const diff = day === 0 ? -6 : 1 - day
  d.setDate(d.getDate() + diff)
  d.setHours(0, 0, 0, 0)
  return d
}

export function getWeekEnd(start: Date): Date {
  const d = new Date(start)
  d.setDate(d.getDate() + 6)
  return d
}

function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export function WeekNavigation({
  weekStart,
  onPrevWeek,
  onNextWeek,
  onCurrentWeek,
}: WeekNavigationProps) {
  const weekEnd = getWeekEnd(weekStart)

  return (
    <div className="flex items-center justify-between mb-4">
      <Button variant="ghost" onClick={onPrevWeek}>
        <ChevronLeft className="w-5 h-5" />
      </Button>
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-semibold text-white">
          {formatDate(weekStart)} &mdash; {formatDate(weekEnd)}
        </h2>
        <Button variant="ghost" size="sm" onClick={onCurrentWeek} className="text-xs text-slate-400">
          Today
        </Button>
      </div>
      <Button variant="ghost" onClick={onNextWeek}>
        <ChevronRight className="w-5 h-5" />
      </Button>
    </div>
  )
}
