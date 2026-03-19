import { Wrench } from 'lucide-react'

interface ToolCallCardProps {
  tools: string[]
}

const TOOL_DISPLAY_NAMES: Record<string, string> = {
  rank_candidates: 'ML Ranking',
  find_open_shifts: 'Shift Search',
  get_employee_info: 'Employee Lookup',
  list_incidents: 'Incident List',
  get_coverage_stats: 'Coverage Stats',
}

export function ToolCallCard({ tools }: ToolCallCardProps) {
  if (tools.length === 0) return null

  return (
    <div className="flex items-center gap-1.5 mt-2 flex-wrap">
      <span className="text-xs text-slate-500">Tools used:</span>
      {tools.map((tool) => (
        <span
          key={tool}
          className="inline-flex items-center gap-1 bg-cyan-500/10 text-cyan-400 text-xs px-2 py-0.5 rounded-full"
        >
          <Wrench className="w-3 h-3" />
          {TOOL_DISPLAY_NAMES[tool] || tool}
        </span>
      ))}
    </div>
  )
}
