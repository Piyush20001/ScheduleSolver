import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../../lib/api-client'
import type { IncidentEnriched, IncidentCreate } from '../../types'

export function useIncidents(status?: string) {
  return useQuery({
    queryKey: ['incidents', status],
    queryFn: () =>
      apiClient.get<IncidentEnriched[]>(
        '/api/incidents',
        status ? { status } : undefined
      ),
  })
}

export function useCreateIncident() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: IncidentCreate) =>
      apiClient.post<IncidentEnriched>('/api/incidents', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
    },
  })
}
