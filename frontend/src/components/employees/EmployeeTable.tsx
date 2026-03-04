import { ChevronUp, ChevronDown } from 'lucide-react'
import { Badge } from '../ui/Badge'
import { ScoreBar } from '../common/ScoreBar'
import type { Employee } from '../../types'

type SortField = 'name' | 'role' | 'skill_level' | 'reliability_score' | 'hours_worked_this_week'
type SortDirection = 'asc' | 'desc'

interface EmployeeTableProps {
  employees: Employee[]
  sortField: SortField | null
  sortDirection: SortDirection
  onSort: (field: SortField) => void
}

interface ColumnDef {
  key: SortField | 'preferences'
  label: string
  sortable: boolean
  width?: string
}

const COLUMNS: ColumnDef[] = [
  { key: 'name', label: 'Name', sortable: true },
  { key: 'role', label: 'Role', sortable: true, width: 'w-[100px]' },
  { key: 'skill_level', label: 'Skill', sortable: true, width: 'w-[80px]' },
  { key: 'reliability_score', label: 'Reliability', sortable: true, width: 'w-[150px]' },
  { key: 'preferences', label: 'Preferences', sortable: false, width: 'w-[140px]' },
  { key: 'hours_worked_this_week', label: 'Hours', sortable: true, width: 'w-[120px]' },
]

const ROLE_DOT_COLORS: Record<string, string> = {
  cook: 'bg-cyan-400',
  server: 'bg-teal-400',
  cashier: 'bg-amber-400',
  host: 'bg-violet-400',
  manager: 'bg-rose-400',
  barista: 'bg-emerald-400',
}

export function EmployeeTable({
  employees,
  sortField,
  sortDirection,
  onSort,
}: EmployeeTableProps) {
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="bg-slate-800/50">
            {COLUMNS.map((col) => (
              <th
                key={col.key}
                className={`text-left text-xs text-slate-400 uppercase tracking-wider px-4 py-3 ${col.width ?? ''} ${
                  col.sortable ? 'cursor-pointer select-none hover:text-slate-200' : ''
                }`}
                onClick={() => {
                  if (col.sortable && col.key !== 'preferences') {
                    onSort(col.key as SortField)
                  }
                }}
              >
                <div className="flex items-center gap-1">
                  <span>{col.label}</span>
                  {col.sortable && col.key !== 'preferences' && sortField === col.key && (
                    sortDirection === 'desc' ? (
                      <ChevronDown className="w-3 h-3" />
                    ) : (
                      <ChevronUp className="w-3 h-3" />
                    )
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {employees.map((employee) => {
            const hoursPercent =
              employee.max_hours_weekly > 0
                ? (employee.hours_worked_this_week / employee.max_hours_weekly) * 100
                : 0
            const hoursWarn = hoursPercent > 80

            return (
              <tr
                key={employee.id}
                className="border-b border-slate-800 hover:bg-slate-800/30 transition-colors"
              >
                <td className="px-4 py-3">
                  <span className="text-sm text-slate-200 font-medium">{employee.name}</span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        ROLE_DOT_COLORS[employee.role.toLowerCase()] ?? 'bg-slate-500'
                      }`}
                    />
                    <span className="text-sm text-slate-300 capitalize">{employee.role}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="text-sm text-slate-300">{employee.skill_level}</span>
                </td>
                <td className="px-4 py-3">
                  <ScoreBar score={employee.reliability_score} />
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1">
                    {employee.prefers_morning && (
                      <Badge className="text-amber-400 border border-amber-400/30 bg-transparent">
                        AM
                      </Badge>
                    )}
                    {employee.prefers_evening && (
                      <Badge className="text-violet-400 border border-violet-400/30 bg-transparent">
                        PM
                      </Badge>
                    )}
                    {employee.weekend_available && (
                      <Badge className="text-cyan-400 border border-cyan-400/30 bg-transparent">
                        WE
                      </Badge>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-sm font-mono ${hoursWarn ? 'text-amber-400' : 'text-slate-300'}`}>
                    {employee.hours_worked_this_week.toFixed(0)} / {employee.max_hours_weekly}
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export type { SortField, SortDirection }
