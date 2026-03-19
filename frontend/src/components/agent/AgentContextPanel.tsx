import { Cpu, Wrench, Zap } from 'lucide-react'
import { Card } from '../ui/Card'
import { Badge } from '../ui/Badge'
import type { AgentStatus } from '../../types'

interface AgentContextPanelProps {
  status: AgentStatus | undefined
  isStatusLoading: boolean
  onQuickPrompt: (prompt: string) => void
  disabled: boolean
}

const TOOLS = [
  { name: 'ML Ranking', desc: 'Rank employees for a shift using XGBoost ML model' },
  { name: 'Shift Search', desc: 'Find open or scheduled shifts by date and role' },
  { name: 'Employee Lookup', desc: 'Get employee details, reliability, and preferences' },
  { name: 'Incident List', desc: 'View active and resolved scheduling incidents' },
  { name: 'Coverage Stats', desc: 'System-wide coverage rate and resolution metrics' },
]

const QUICK_PROMPTS = [
  'Who should cover the next open shift?',
  "Show me today's open shifts",
  'Who is our most reliable employee?',
  'Any active incidents right now?',
  'How is our coverage rate?',
]

export function AgentContextPanel({
  status,
  isStatusLoading,
  onQuickPrompt,
  disabled,
}: AgentContextPanelProps) {
  return (
    <div className="space-y-4">
      {/* Agent Status Card */}
      <Card>
        <div className="flex items-center gap-2 mb-3">
          <Cpu className="w-4 h-4 text-slate-400" />
          <h3 className="text-sm font-medium text-slate-300">Agent Status</h3>
        </div>
        {isStatusLoading ? (
          <div className="h-4 w-24 bg-slate-700 rounded animate-pulse" />
        ) : (
          <>
            <div className="flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  status?.available ? 'bg-emerald-400' : 'bg-amber-400'
                }`}
              />
              <span className="text-sm text-slate-300">
                {status?.available ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            {status?.model && (
              <p className="text-xs font-mono text-slate-400 mt-1">Model: {status.model}</p>
            )}
            {!status?.available && (
              <p className="text-xs text-slate-500 mt-1">Ollama not running</p>
            )}
            <Badge
              variant={status?.available ? 'success' : 'warning'}
              size="sm"
              className="mt-2"
            >
              {status?.tools_count || 5} tools available
            </Badge>
          </>
        )}
      </Card>

      {/* Available Tools */}
      <Card>
        <div className="flex items-center gap-2 mb-3">
          <Wrench className="w-4 h-4 text-slate-400" />
          <h3 className="text-sm font-medium text-slate-300">Available Tools</h3>
        </div>
        <div className="divide-y divide-slate-700/50">
          {TOOLS.map((tool) => (
            <div key={tool.name} className="py-2 first:pt-0 last:pb-0">
              <p className="text-sm font-medium text-slate-200">{tool.name}</p>
              <p className="text-xs text-slate-500">{tool.desc}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Quick Prompts */}
      <Card>
        <div className="flex items-center gap-2 mb-3">
          <Zap className="w-4 h-4 text-slate-400" />
          <h3 className="text-sm font-medium text-slate-300">Quick Prompts</h3>
        </div>
        <div className="space-y-1">
          {QUICK_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              onClick={() => onQuickPrompt(prompt)}
              disabled={disabled}
              className="w-full text-left text-sm text-slate-300 hover:text-white hover:bg-white/5 rounded-lg px-3 py-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {prompt}
            </button>
          ))}
        </div>
      </Card>
    </div>
  )
}
