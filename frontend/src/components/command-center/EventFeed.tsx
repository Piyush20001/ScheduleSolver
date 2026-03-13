import { useState, useEffect, useRef } from 'react'
import { Terminal, ChevronDown } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '../ui/Card'
import { Badge } from '../ui/Badge'
import type { WebSocketEvent } from '../../hooks/useDemoFlow'

interface EventFeedProps {
  events: WebSocketEvent[]
}

function getEventTypeVariant(type: string): 'info' | 'warning' | 'success' | 'danger' | 'default' {
  switch (type) {
    case 'incident_created':
      return 'info'
    case 'calling_candidate':
      return 'warning'
    case 'call_result':
      return 'success'
    case 'incident_resolved':
      return 'success'
    case 'incident_escalated':
      return 'danger'
    default:
      return 'default'
  }
}

function formatEventType(type: string): string {
  return type.replace(/_/g, ' ')
}

export function EventFeed({ events }: EventFeedProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (isExpanded) {
      scrollRef.current?.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      })
    }
  }, [events.length, isExpanded])

  return (
    <Card>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between w-full"
      >
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span className="text-sm font-medium text-slate-400 uppercase tracking-wider">
            Event Log
          </span>
          {events.length > 0 && (
            <Badge variant="default" size="sm">
              {events.length}
            </Badge>
          )}
        </div>
        <ChevronDown
          className={`w-4 h-4 text-slate-400 transition-transform ${
            isExpanded ? 'rotate-180' : ''
          }`}
        />
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div
              ref={scrollRef}
              className="mt-3 max-h-60 overflow-y-auto font-mono text-xs space-y-1 bg-slate-950 rounded-lg p-3"
            >
              {events.length === 0 && (
                <p className="text-slate-600 text-center py-4">No events yet</p>
              )}
              {events.map((event, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-slate-600 flex-shrink-0">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                  <Badge variant={getEventTypeVariant(event.type)} size="sm">
                    {formatEventType(event.type)}
                  </Badge>
                  <span className="text-slate-400 truncate">
                    {JSON.stringify(event.data).slice(0, 80)}
                    {JSON.stringify(event.data).length > 80 ? '...' : ''}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  )
}
