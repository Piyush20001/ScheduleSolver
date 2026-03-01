import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../lib/api-client'
import type { Employee } from '../../types'

interface EmployeeFilters {
  role?: string
  weekend_available?: boolean
  min_reliability?: number
}

export function useEmployees(filters?: EmployeeFilters) {
  return useQuery({
    queryKey: ['employees', filters],
    queryFn: () =>
      apiClient.get<Employee[]>(
        '/api/employees',
        filters as Record<string, string | number | boolean | undefined>
      ),
  })
}
