export interface CandidateRanking {
  employee_id: number
  name: string
  role: string
  score: number
  reason: string
}

export interface RankRequest {
  shift_id: number
}

export interface RankResponse {
  shift_id: number
  role_required: string
  candidates: CandidateRanking[]
}
