export interface ModelInfo {
  roc_auc: number
  accuracy: number
  precision: number
  recall: number
  feature_importances: Record<string, number>
}

export interface CoverageStats {
  avg_calls_to_resolution: number
  resolution_rate_percent: number
  avg_time_to_cover_seconds: number
}

export interface EmployeePerformance {
  employee_id: number
  name: string
  role: string
  total_calls: number
  accepted_calls: number
  acceptance_rate: number
}
