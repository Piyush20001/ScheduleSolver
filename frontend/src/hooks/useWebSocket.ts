import { useCallback, useEffect, useRef, useState } from 'react'
import type { WSEvent } from '../types'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'reconnecting'

interface UseWebSocketOptions {
  url?: string
  onEvent?: (event: WSEvent) => void
  onMessage?: (data: unknown) => void
  maxReconnectAttempts?: number
  enabled?: boolean
}

interface UseWebSocketReturn {
  status: ConnectionStatus
  lastEvent: WSEvent | null
  sendMessage: (message: string) => void
  reconnect: () => void
}

export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const {
    url = WS_URL,
    onEvent,
    onMessage,
    maxReconnectAttempts = 10,
    enabled = true,
  } = options

  const [status, setStatus] = useState<ConnectionStatus>('disconnected')
  const [lastEvent, setLastEvent] = useState<WSEvent | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const attemptsRef = useRef(0)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const keepaliveRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const onEventRef = useRef(onEvent)
  const onMessageRef = useRef(onMessage)

  // Keep callback refs current without triggering reconnects
  useEffect(() => {
    onEventRef.current = onEvent
  }, [onEvent])

  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (keepaliveRef.current) {
      clearInterval(keepaliveRef.current)
      keepaliveRef.current = null
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    setStatus('connecting')

    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      setStatus('connected')
      attemptsRef.current = 0

      // Start keepalive ping every 30 seconds
      keepaliveRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send('ping')
        }
      }, 30000)
    }

    ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data) as WSEvent
        setLastEvent(parsed)
        onEventRef.current?.(parsed)
        onMessageRef.current?.(parsed)
      } catch {
        // Non-JSON message (e.g., pong), ignore
        onMessageRef.current?.(event.data)
      }
    }

    ws.onclose = () => {
      setStatus('disconnected')
      wsRef.current = null

      if (keepaliveRef.current) {
        clearInterval(keepaliveRef.current)
        keepaliveRef.current = null
      }

      // Auto-reconnect with exponential backoff
      if (attemptsRef.current < maxReconnectAttempts) {
        setStatus('reconnecting')
        const delay = Math.min(1000 * 2 ** attemptsRef.current, 30000)
        attemptsRef.current += 1
        reconnectTimeoutRef.current = setTimeout(() => {
          connect()
        }, delay)
      }
    }

    ws.onerror = () => {
      // onclose will fire after onerror, so reconnection is handled there
    }
  }, [url, maxReconnectAttempts])

  const sendMessage = useCallback((message: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(message)
    } else {
      console.warn('WebSocket is not connected. Cannot send message.')
    }
  }, [])

  const reconnect = useCallback(() => {
    disconnect()
    attemptsRef.current = 0
    connect()
  }, [disconnect, connect])

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    if (enabled) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [enabled, connect, disconnect])

  return { status, lastEvent, sendMessage, reconnect }
}
