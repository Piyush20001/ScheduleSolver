export interface CallLog {
  id: number
  incident_id: number
  employee_id: number
  call_order: number
  status: string
  ml_score: number
  call_started_at: string
  call_ended_at: string | null
  duration_seconds: number | null
  notes: string | null
}
