export interface Shift {
  id: number
  date: string
  start_time: string
  end_time: string
  shift_type: string
  role_required: string
  min_skill_level: number
  is_weekend: boolean
  status: string
  assigned_employee_id: number | null
}

export interface ShiftEnriched extends Shift {
  assigned_employee_name: string | null
}
