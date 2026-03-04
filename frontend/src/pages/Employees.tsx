import { useState, useMemo } from 'react'
import { Users } from 'lucide-react'
import { Badge } from '../components/ui/Badge'
import { SkeletonTable } from '../components/ui/Skeleton'
import { ErrorCard } from '../components/ui/ErrorCard'
import { EmptyState } from '../components/ui/EmptyState'
import { useEmployees } from '../hooks/api'
import { EmployeeFilters } from '../components/employees/EmployeeFilters'
import { EmployeeTable } from '../components/employees/EmployeeTable'
import type { SortField, SortDirection } from '../components/employees/EmployeeTable'

export default function Employees() {
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [weekendFilter, setWeekendFilter] = useState<boolean | null>(null)
  const [minReliability, setMinReliability] = useState<number | null>(null)
  const [sortField, setSortField] = useState<SortField | null>(null)
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')

  const { data: employees, isLoading, isError, error, refetch } = useEmployees({
    role: roleFilter || undefined,
    weekend_available: weekendFilter ?? undefined,
    min_reliability: minReliability ?? undefined,
  })

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      if (sortDirection === 'desc') {
        setSortDirection('asc')
      } else {
        setSortField(null)
        setSortDirection('desc')
      }
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const filteredAndSorted = useMemo(() => {
    if (!employees) return []

    let result = [...employees]

    // Client-side search filter
    if (search.trim()) {
      const q = search.toLowerCase()
      result = result.filter(
        (emp) =>
          emp.name.toLowerCase().includes(q) || emp.role.toLowerCase().includes(q)
      )
    }

    // Client-side sort
    if (sortField) {
      result.sort((a, b) => {
        const aVal = a[sortField]
        const bVal = b[sortField]
        if (typeof aVal === 'string' && typeof bVal === 'string') {
          return sortDirection === 'asc'
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal)
        }
        if (typeof aVal === 'number' && typeof bVal === 'number') {
          return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
        }
        return 0
      })
    }

    return result
  }, [employees, search, sortField, sortDirection])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="w-6 h-6 text-cyan-400" />
          <div>
            <h1 className="text-2xl font-bold text-white">Employees</h1>
            <p className="text-slate-400 text-sm mt-0.5">
              Search, filter, and view all employees with reliability scores and preferences
            </p>
          </div>
        </div>
        {employees && (
          <Badge variant="info" size="md">
            {employees.length} total
          </Badge>
        )}
      </div>

      <EmployeeFilters
        search={search}
        onSearchChange={setSearch}
        roleFilter={roleFilter}
        onRoleFilterChange={setRoleFilter}
        weekendFilter={weekendFilter}
        onWeekendFilterChange={setWeekendFilter}
        minReliability={minReliability}
        onMinReliabilityChange={setMinReliability}
      />

      {isLoading && <SkeletonTable rows={8} columns={6} />}

      {isError && (
        <ErrorCard
          message={error instanceof Error ? error.message : 'Failed to load employees'}
          onRetry={() => refetch()}
        />
      )}

      {!isLoading && !isError && filteredAndSorted.length === 0 && (
        <EmptyState
          icon={<Users className="w-10 h-10" />}
          title="No employees found"
          description="Try adjusting your search or filter criteria"
        />
      )}

      {!isLoading && !isError && filteredAndSorted.length > 0 && (
        <EmployeeTable
          employees={filteredAndSorted}
          sortField={sortField}
          sortDirection={sortDirection}
          onSort={handleSort}
        />
      )}
    </div>
  )
}
