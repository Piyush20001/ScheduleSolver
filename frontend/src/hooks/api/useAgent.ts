import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '../../lib/api-client'
import type { AgentStatus, AgentChatRequest, AgentChatResponse } from '../../types'

export function useAgentStatus() {
  return useQuery({
    queryKey: ['agent', 'status'],
    queryFn: () => apiClient.get<AgentStatus>('/api/agent/status'),
    refetchInterval: 30_000, // Poll every 30 seconds (D-08)
  })
}

export function useAgentChat() {
  return useMutation({
    mutationFn: (data: AgentChatRequest) =>
      apiClient.post<AgentChatResponse>('/api/agent/chat', data),
  })
}
