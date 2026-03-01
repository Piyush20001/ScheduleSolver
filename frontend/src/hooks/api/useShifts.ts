import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../lib/api-client'
import type { ShiftEnriched } from '../../types'

interface ShiftFilters {
  start_date?: string
  end_date?: string
}

export function useShifts(filters?: ShiftFilters) {
  return useQuery({
    queryKey: ['shifts', filters],
    queryFn: () =>
      apiClient.get<ShiftEnriched[]>(
        '/api/shifts',
        filters as Record<string, string | number | boolean | undefined>
      ),
  })
}
