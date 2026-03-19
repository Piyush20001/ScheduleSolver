import { useState } from 'react'
import { AlertTriangle } from 'lucide-react'
import { useAgentStatus, useAgentChat } from '../hooks/api'
import { ChatInterface } from '../components/agent/ChatInterface'
import { AgentContextPanel } from '../components/agent/AgentContextPanel'
import type { ChatMessage } from '../types'

export default function Agent() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const { data: status, isLoading: statusLoading } = useAgentStatus()
  const chatMutation = useAgentChat()
  const isAvailable = status?.available ?? false

  function handleSendMessage(text: string) {
    // Add user message to state
    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])

    // Build history from existing messages (for context)
    const history = messages.map((m) => ({
      role: m.role as 'user' | 'assistant',
      content: m.content,
    }))

    // Send to backend
    chatMutation.mutate(
      { message: text, history },
      {
        onSuccess: (data) => {
          const agentMsg: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: data.response,
            tools_used: data.tools_used,
            timestamp: new Date(),
          }
          setMessages((prev) => [...prev, agentMsg])
        },
        onError: (error) => {
          const errorMsg: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
            timestamp: new Date(),
          }
          setMessages((prev) => [...prev, errorMsg])
        },
      },
    )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)]">
      {/* Page header */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-white">AI Agent</h1>
        <p className="text-slate-400 mt-1">Natural language interface powered by Ollama</p>
      </div>

      {/* Fallback banner when Ollama unavailable (AGNT-07) */}
      {!statusLoading && !isAvailable && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 mb-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-amber-300">
                AI Agent requires Ollama
              </h3>
              <p className="text-sm text-slate-400 mt-1">
                To enable the AI Agent, follow these steps:
              </p>
              <ol className="text-sm text-slate-400 mt-2 space-y-1 list-decimal list-inside">
                <li>
                  Install Ollama from{' '}
                  <span className="text-cyan-400 font-mono">ollama.com</span>
                </li>
                <li>
                  Pull a model:{' '}
                  <code className="bg-slate-800 px-1.5 py-0.5 rounded text-cyan-400 font-mono text-xs">
                    ollama pull qwen2.5:7b
                  </code>
                </li>
                <li>
                  Start Ollama:{' '}
                  <code className="bg-slate-800 px-1.5 py-0.5 rounded text-cyan-400 font-mono text-xs">
                    ollama serve
                  </code>
                </li>
              </ol>
              <p className="text-xs text-slate-500 mt-2">
                Checking for Ollama every 30 seconds...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Main content: 70/30 split */}
      <div className="flex gap-4 flex-1 min-h-0">
        {/* Chat Interface (70%) */}
        <div className="flex-[7] bg-slate-800/30 border border-slate-700/50 rounded-xl overflow-hidden">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={chatMutation.isPending}
            disabled={!isAvailable}
          />
        </div>

        {/* Context Panel (30%) */}
        <div className="flex-[3] overflow-y-auto">
          <AgentContextPanel
            status={status}
            isStatusLoading={statusLoading}
            onQuickPrompt={handleSendMessage}
            disabled={!isAvailable}
          />
        </div>
      </div>
    </div>
  )
}
