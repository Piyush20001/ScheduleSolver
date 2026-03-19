/** GET /api/agent/status response */
export interface AgentStatus {
  available: boolean
  model: string | null
  tools_count: number
}

/** Chat history message sent to backend */
export interface AgentChatHistoryMessage {
  role: 'user' | 'assistant'
  content: string
}

/** POST /api/agent/chat request body */
export interface AgentChatRequest {
  message: string
  history: AgentChatHistoryMessage[]
}

/** POST /api/agent/chat response */
export interface AgentChatResponse {
  response: string
  tools_used: string[]
  ollama_available: boolean
}

/** Internal UI chat message state */
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  tools_used?: string[]
  timestamp: Date
}
