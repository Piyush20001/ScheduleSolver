import { useState } from 'react'
import { Calendar } from 'lucide-react'
import { SkeletonTable } from '../components/ui/Skeleton'
import { ErrorCard } from '../components/ui/ErrorCard'
import { useShifts } from '../hooks/api'
import { WeekNavigation, getWeekStart } from '../components/schedule/WeekNavigation'
import { WeekGrid } from '../components/schedule/WeekGrid'
import { CandidatePanel } from '../components/schedule/CandidatePanel'
import type { ShiftEnriched } from '../types'

export default function Schedule() {
  const [weekStart, setWeekStart] = useState<Date>(() => getWeekStart(new Date()))
  const [selectedShift, setSelectedShift] = useState<ShiftEnriched | null>(null)

  const startDateISO = weekStart.toISOString().split('T')[0]
  const endDate = new Date(weekStart)
  endDate.setDate(endDate.getDate() + 6)
  const endDateISO = endDate.toISOString().split('T')[0]

  const { data: shifts, isLoading, isError, error, refetch } = useShifts({
    start_date: startDateISO,
    end_date: endDateISO,
  })

  const handlePrevWeek = () => {
    setWeekStart((prev) => {
      const d = new Date(prev)
      d.setDate(d.getDate() - 7)
      return d
    })
  }

  const handleNextWeek = () => {
    setWeekStart((prev) => {
      const d = new Date(prev)
      d.setDate(d.getDate() + 7)
      return d
    })
  }

  const handleCurrentWeek = () => {
    setWeekStart(getWeekStart(new Date()))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Calendar className="w-6 h-6 text-cyan-400" />
        <div>
          <h1 className="text-2xl font-bold text-white">Schedule</h1>
          <p className="text-slate-400 text-sm mt-0.5">
            Weekly shift grid with coverage status and ML recommendations
          </p>
        </div>
      </div>

      <WeekNavigation
        weekStart={weekStart}
        onPrevWeek={handlePrevWeek}
        onNextWeek={handleNextWeek}
        onCurrentWeek={handleCurrentWeek}
      />

      {isLoading && <SkeletonTable rows={3} columns={8} />}

      {isError && (
        <ErrorCard
          message={error instanceof Error ? error.message : 'Failed to load shifts'}
          onRetry={() => refetch()}
        />
      )}

      {!isLoading && !isError && shifts && (
        <WeekGrid
          shifts={shifts}
          weekStart={weekStart}
          onShiftClick={(shift) => setSelectedShift(shift)}
        />
      )}

      <CandidatePanel
        shift={selectedShift}
        onClose={() => setSelectedShift(null)}
      />
    </div>
  )
}
