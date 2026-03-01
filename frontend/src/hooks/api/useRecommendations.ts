import { useMutation } from '@tanstack/react-query'
import { apiClient } from '../../lib/api-client'
import type { RankRequest, RankResponse } from '../../types'

export function useRankCandidates() {
  return useMutation({
    mutationFn: (data: RankRequest) =>
      apiClient.post<RankResponse>('/api/recommendations/rank', data),
  })
}
