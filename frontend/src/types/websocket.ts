export type WSEventType =
  | 'incident_created'
  | 'calling_candidate'
  | 'call_result'
  | 'incident_resolved'
  | 'incident_escalated'

export interface WSEvent<T = unknown> {
  type: WSEventType
  timestamp: string
  data: T
}
