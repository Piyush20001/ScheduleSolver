export interface Employee {
  id: number
  name: string
  email: string
  phone: string
  role: string
  skill_level: number
  reliability_score: number
  prefers_morning: boolean
  prefers_evening: boolean
  weekend_available: boolean
  max_hours_weekly: number
  is_active: boolean
  hired_date: string
  hours_worked_this_week: number
}

export interface EmployeeCreate {
  name: string
  email: string
  phone: string
  role: string
  skill_level?: number
  reliability_score?: number
  prefers_morning?: boolean
  prefers_evening?: boolean
  weekend_available?: boolean
  max_hours_weekly?: number
  is_active?: boolean
  hired_date: string
}
