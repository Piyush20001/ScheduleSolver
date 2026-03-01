export interface Incident {
  id: number
  incident_id: string
  shift_id: number
  original_employee_id: number
  reason: string
  urgency: string
  status: string
  replacement_employee_id: number | null
  created_at: string
  resolved_at: string | null
}

export interface IncidentEnriched extends Incident {
  original_employee_name: string
  shift_date: string | null
  shift_type: string | null
  role_required: string | null
}

export interface IncidentCreate {
  shift_id: number
  original_employee_id: number
  reason: string
  urgency: string
}
