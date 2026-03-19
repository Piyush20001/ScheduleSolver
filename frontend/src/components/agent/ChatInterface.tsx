import { useState, useRef, useEffect } from 'react'
import { Send, Bot } from 'lucide-react'
import { Button } from '../ui/Button'
import { ToolCallCard } from './ToolCallCard'
import type { ChatMessage } from '../../types'

interface ChatInterfaceProps {
  messages: ChatMessage[]
  onSendMessage: (message: string) => void
  isLoading: boolean
  disabled: boolean
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] ${
          isUser
            ? 'bg-cyan-600/20 rounded-xl rounded-br-none'
            : 'bg-slate-700/50 rounded-xl rounded-bl-none'
        } px-4 py-3`}
      >
        <p className="text-sm text-slate-200 whitespace-pre-wrap">{message.content}</p>
        {!isUser && message.tools_used && (
          <ToolCallCard tools={message.tools_used} />
        )}
        <p className="text-xs text-slate-500 mt-1.5">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex items-center gap-1.5 bg-slate-700/50 rounded-xl rounded-bl-none px-4 py-3 w-fit">
        <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:0ms]" />
        <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:150ms]" />
        <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:300ms]" />
      </div>
    </div>
  )
}

function EmptyChat() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center text-center py-12">
      <Bot className="w-12 h-12 text-slate-600 mb-4" />
      <h3 className="text-lg font-medium text-slate-300 mb-1">ScheduleSolver AI</h3>
      <p className="text-sm text-slate-500 max-w-sm">
        Ask me about shifts, employees, incidents, or coverage statistics.
      </p>
    </div>
  )
}

export function ChatInterface({ messages, onSendMessage, isLoading, disabled }: ChatInterfaceProps) {
  const [input, setInput] = useState('')
  const scrollAnchorRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    scrollAnchorRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = input.trim()
    if (!trimmed || disabled || isLoading) return
    onSendMessage(trimmed)
    setInput('')
    inputRef.current?.focus()
  }

  return (
    <div className="flex flex-col h-full">
      {/* Message list */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && !isLoading && <EmptyChat />}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={scrollAnchorRef} />
      </div>

      {/* Input bar */}
      <div className="border-t border-slate-700/50 p-4">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              disabled
                ? 'AI Agent requires Ollama...'
                : 'Ask about shifts, employees, or coverage...'
            }
            disabled={disabled || isLoading}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50 disabled:opacity-50"
          />
          <Button
            type="submit"
            disabled={disabled || isLoading || !input.trim()}
            loading={isLoading}
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}
