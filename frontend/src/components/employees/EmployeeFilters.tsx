import { Search } from 'lucide-react'

interface EmployeeFiltersProps {
  search: string
  onSearchChange: (value: string) => void
  roleFilter: string
  onRoleFilterChange: (value: string) => void
  weekendFilter: boolean | null
  onWeekendFilterChange: (value: boolean | null) => void
  minReliability: number | null
  onMinReliabilityChange: (value: number | null) => void
}

const ROLES = ['cook', 'server', 'cashier', 'host', 'manager', 'barista']
const RELIABILITY_OPTIONS = [
  { label: 'Any Reliability', value: '' },
  { label: '0.5+', value: '0.5' },
  { label: '0.6+', value: '0.6' },
  { label: '0.7+', value: '0.7' },
  { label: '0.8+', value: '0.8' },
  { label: '0.9+', value: '0.9' },
]

export function EmployeeFilters({
  search,
  onSearchChange,
  roleFilter,
  onRoleFilterChange,
  weekendFilter,
  onWeekendFilterChange,
  minReliability,
  onMinReliabilityChange,
}: EmployeeFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Search input */}
      <div className="relative flex-1 min-w-[200px]">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search employees..."
          className="w-full bg-slate-800 border border-slate-700 text-white placeholder-slate-500 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50"
        />
      </div>

      {/* Role dropdown */}
      <select
        value={roleFilter}
        onChange={(e) => onRoleFilterChange(e.target.value)}
        className="bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
      >
        <option value="">All Roles</option>
        {ROLES.map((role) => (
          <option key={role} value={role} className="capitalize">
            {role.charAt(0).toUpperCase() + role.slice(1)}
          </option>
        ))}
      </select>

      {/* Weekend toggle */}
      <button
        onClick={() => {
          if (weekendFilter === null) onWeekendFilterChange(true)
          else onWeekendFilterChange(null)
        }}
        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
          weekendFilter !== null
            ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500'
            : 'bg-slate-800 text-slate-400 border border-slate-700 hover:text-white'
        }`}
      >
        {weekendFilter !== null ? 'Weekend' : 'All Days'}
      </button>

      {/* Min reliability dropdown */}
      <select
        value={minReliability !== null ? String(minReliability) : ''}
        onChange={(e) =>
          onMinReliabilityChange(e.target.value ? parseFloat(e.target.value) : null)
        }
        className="bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
      >
        {RELIABILITY_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  )
}
