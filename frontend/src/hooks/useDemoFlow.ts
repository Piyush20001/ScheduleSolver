import { useCallback, useRef, useState } from 'react'
import { useWebSocket } from './useWebSocket'
import type { WSEvent } from '../types'

export interface CallAttempt {
  callOrder: number
  totalCandidates: number
  employeeId: number
  name: string
  role: string
  mlScore: number
  reason: string
  status: 'ringing' | 'accepted' | 'declined' | 'no_answer' | 'voicemail'
  durationSeconds?: number
}

export interface WebSocketEvent {
  type: string
  timestamp: string
  data: Record<string, unknown>
}

export interface DemoState {
  status: 'idle' | 'creating' | 'calling' | 'resolved' | 'escalated'
  incidentId: string | null
  calls: CallAttempt[]
  events: WebSocketEvent[]
  resolution: {
    replacementName: string
    replacementRole: string
    totalCalls: number
  } | null
  error: string | null
}

const INITIAL_STATE: DemoState = {
  status: 'idle',
  incidentId: null,
  calls: [],
  events: [],
  resolution: null,
  error: null,
}

export function useDemoFlow() {
  const [state, setState] = useState<DemoState>(INITIAL_STATE)
  const stateRef = useRef(state)
  stateRef.current = state

  const handleEvent = useCallback((evt: WSEvent) => {
    const msg = evt as WSEvent & { incident_id?: string; data?: Record<string, unknown> }

    // Only process events for our active incident
    if (stateRef.current.incidentId && msg.incident_id !== stateRef.current.incidentId) return

    // Only process known event types
    const knownTypes = ['incident_created', 'calling_candidate', 'call_result', 'incident_resolved', 'incident_escalated']
    if (!knownTypes.includes(msg.type)) return

    const eventData = (msg.data ?? {}) as Record<string, unknown>
    const event: WebSocketEvent = {
      type: msg.type,
      timestamp: msg.timestamp,
      data: eventData,
    }

    switch (msg.type) {
      case 'incident_created':
        setState((prev) => ({
          ...prev,
          status: 'calling',
          events: [...prev.events, event],
        }))
        break

      case 'calling_candidate':
        setState((prev) => ({
          ...prev,
          calls: [
            ...prev.calls,
            {
              callOrder: eventData.call_order as number,
              totalCandidates: eventData.total_candidates as number,
              employeeId: eventData.employee_id as number,
              name: eventData.name as string,
              role: eventData.role as string,
              mlScore: eventData.ml_score as number,
              reason: eventData.reason as string,
              status: 'ringing',
            },
          ],
          events: [...prev.events, event],
        }))
        break

      case 'call_result':
        setState((prev) => ({
          ...prev,
          calls: prev.calls.map((c) =>
            c.callOrder === (eventData.call_order as number)
              ? {
                  ...c,
                  status: eventData.outcome as CallAttempt['status'],
                  durationSeconds: eventData.duration_seconds as number,
                }
              : c
          ),
          events: [...prev.events, event],
        }))
        break

      case 'incident_resolved':
        setState((prev) => ({
          ...prev,
          status: 'resolved',
          resolution: {
            replacementName: eventData.replacement_name as string,
            replacementRole: eventData.replacement_role as string,
            totalCalls: eventData.total_calls as number,
          },
          events: [...prev.events, event],
        }))
        break

      case 'incident_escalated':
        setState((prev) => ({
          ...prev,
          status: 'escalated',
          events: [...prev.events, event],
        }))
        break
    }
  }, [])

  useWebSocket({ onEvent: handleEvent })

  // Keep a second effect-based approach as backup for lastEvent changes
  // Not needed since we use onEvent callback, but kept for safety

  const triggerDemo = useCallback(async () => {
    setState({ ...INITIAL_STATE, status: 'creating' })

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

      // 1. Find a scheduled shift with an assigned employee
      const shiftsRes = await fetch(`${API_URL}/api/shifts/`)
      if (!shiftsRes.ok) {
        setState((prev) => ({ ...prev, status: 'idle', error: 'Failed to fetch shifts' }))
        return
      }

      const shifts = (await shiftsRes.json()) as Array<{
        id: number
        status: string
        assigned_employee_id: number | null
      }>

      const scheduledShift = shifts.find(
        (s) => s.status === 'scheduled' && s.assigned_employee_id != null
      )

      if (!scheduledShift) {
        setState((prev) => ({
          ...prev,
          status: 'idle',
          error: 'No scheduled shifts available for demo',
        }))
        return
      }

      // 2. Create incident on that shift
      const incidentRes = await fetch(`${API_URL}/api/incidents/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          shift_id: scheduledShift.id,
          original_employee_id: scheduledShift.assigned_employee_id,
          reason: 'Demo: Emergency callout',
          urgency: 'high',
        }),
      })

      if (!incidentRes.ok) {
        setState((prev) => ({
          ...prev,
          status: 'idle',
          error: 'Failed to create demo incident',
        }))
        return
      }

      const incident = (await incidentRes.json()) as { incident_id: string }
      setState((prev) => ({ ...prev, incidentId: incident.incident_id }))

      // Backend automatically spawns calling simulation via asyncio.create_task
      // WebSocket events will flow in and be handled by the onEvent callback
    } catch {
      setState((prev) => ({
        ...prev,
        status: 'idle',
        error: 'Network error triggering demo',
      }))
    }
  }, [])

  const reset = useCallback(() => {
    setState(INITIAL_STATE)
  }, [])

  return { state, triggerDemo, reset }
}
