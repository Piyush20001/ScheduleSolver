import React from 'react'
import { ShiftCell } from './ShiftCell'
import type { ShiftEnriched } from '../../types'

interface WeekGridProps {
  shifts: ShiftEnriched[]
  weekStart: Date
  onShiftClick: (shift: ShiftEnriched) => void
}

const PERIODS = ['morning', 'afternoon', 'evening'] as const
const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] as const

function isSameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  )
}

function buildGrid(
  shifts: ShiftEnriched[],
  weekStart: Date
): Record<string, Record<string, ShiftEnriched | null>> {
  const grid: Record<string, Record<string, ShiftEnriched | null>> = {}
  for (let i = 0; i < 7; i++) {
    const d = new Date(weekStart)
    d.setDate(d.getDate() + i)
    const key = d.toISOString().split('T')[0]
    grid[key] = { morning: null, afternoon: null, evening: null }
  }
  for (const shift of shifts) {
    const dateKey = shift.date
    if (grid[dateKey] && grid[dateKey][shift.shift_type] === null) {
      grid[dateKey][shift.shift_type] = shift
    }
  }
  return grid
}

export function WeekGrid({ shifts, weekStart, onShiftClick }: WeekGridProps) {
  const grid = buildGrid(shifts, weekStart)
  const today = new Date()

  return (
    <div className="grid grid-cols-8 gap-2">
      {/* Header row */}
      <div />
      {DAYS.map((day, i) => {
        const d = new Date(weekStart)
        d.setDate(d.getDate() + i)
        const isToday = isSameDay(d, today)
        return (
          <div
            key={day}
            className={`text-center py-2 text-sm font-medium ${
              isToday ? 'text-cyan-400' : 'text-slate-400'
            }`}
          >
            <div>{day}</div>
            <div className="text-xs text-slate-500">{d.getDate()}</div>
          </div>
        )
      })}

      {/* Period rows */}
      {PERIODS.map((period) => (
        <React.Fragment key={period}>
          <div className="flex items-center text-xs text-slate-500 capitalize font-medium">
            {period}
          </div>
          {Array.from({ length: 7 }, (_, i) => {
            const d = new Date(weekStart)
            d.setDate(d.getDate() + i)
            const dateKey = d.toISOString().split('T')[0]
            const shift = grid[dateKey]?.[period] ?? null
            return (
              <ShiftCell
                key={`${dateKey}-${period}`}
                shift={shift}
                onClick={
                  shift?.status === 'open' ? () => onShiftClick(shift) : undefined
                }
              />
            )
          })}
        </React.Fragment>
      ))}
    </div>
  )
}
