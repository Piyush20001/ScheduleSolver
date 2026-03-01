import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../lib/api-client'
import type { ModelInfo, CoverageStats, EmployeePerformance } from '../../types'

export function useModelInfo() {
  return useQuery({
    queryKey: ['analytics', 'model-info'],
    queryFn: () => apiClient.get<ModelInfo>('/api/analytics/model-info'),
  })
}

export function useCoverageStats() {
  return useQuery({
    queryKey: ['analytics', 'coverage-stats'],
    queryFn: () => apiClient.get<CoverageStats>('/api/analytics/coverage-stats'),
  })
}

export function useEmployeePerformance() {
  return useQuery({
    queryKey: ['analytics', 'employee-performance'],
    queryFn: () =>
      apiClient.get<EmployeePerformance[]>('/api/analytics/employee-performance'),
  })
}
