import { Medal } from 'lucide-react'
import { motion } from 'framer-motion'
import { Card } from '../ui/Card'
import type { CallAttempt, DemoState } from '../../hooks/useDemoFlow'

interface CandidateRankingProps {
  calls: CallAttempt[]
  demoStatus: DemoState['status']
}

function getScoreGradient(score: number): string {
  if (score >= 0.8) return 'linear-gradient(to right, #10b981, #34d399)'
  if (score >= 0.5) return 'linear-gradient(to right, #f59e0b, #fbbf24)'
  return 'linear-gradient(to right, #f43f5e, #fb7185)'
}

function CallStatusBadge({ status }: { status: CallAttempt['status'] }) {
  const configs: Record<
    CallAttempt['status'],
    { dotColor: string; label: string; textColor: string }
  > = {
    ringing: { dotColor: 'bg-cyan-400', label: 'Calling...', textColor: 'text-cyan-400' },
    accepted: { dotColor: 'bg-emerald-400', label: 'Accepted', textColor: 'text-emerald-400' },
    declined: { dotColor: 'bg-rose-400', label: 'Declined', textColor: 'text-rose-400' },
    no_answer: { dotColor: 'bg-slate-400', label: 'No Answer', textColor: 'text-slate-400' },
    voicemail: { dotColor: 'bg-amber-400', label: 'Voicemail', textColor: 'text-amber-400' },
  }

  const config = configs[status]

  return (
    <div className={`flex items-center gap-1.5 ${config.textColor}`}>
      {status === 'ringing' ? (
        <motion.div
          className={`w-2 h-2 rounded-full ${config.dotColor}`}
          animate={{ opacity: [1, 0.3, 1] }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      ) : (
        <div className={`w-2 h-2 rounded-full ${config.dotColor}`} />
      )}
      <span className="text-xs font-medium">{config.label}</span>
    </div>
  )
}

export function CandidateRanking({ calls, demoStatus }: CandidateRankingProps) {
  return (
    <Card>
      <div className="flex items-center gap-2 mb-4">
        <Medal className="w-5 h-5 text-cyan-400" />
        <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
          ML Ranking
        </h3>
      </div>

      {demoStatus === 'idle' && calls.length === 0 && (
        <div className="flex items-center justify-center py-12 text-center">
          <p className="text-sm text-slate-500">Candidates will appear here during demo</p>
        </div>
      )}

      <div className="space-y-3">
        {calls.map((call) => (
          <div
            key={call.callOrder}
            className="p-3 rounded-lg bg-slate-800/30 border border-slate-700/50"
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500 font-mono">#{call.callOrder}</span>
                <span className="text-sm font-medium text-white">{call.name}</span>
              </div>
              <CallStatusBadge status={call.status} />
            </div>

            {/* Gradient score bar */}
            <div className="mt-2">
              <div className="flex items-center gap-2">
                <div className="flex-1 h-3 bg-slate-700 rounded-full overflow-hidden">
                  <motion.div
                    className="h-3 rounded-full"
                    style={{ background: getScoreGradient(call.mlScore) }}
                    initial={{ width: 0 }}
                    animate={{ width: `${call.mlScore * 100}%` }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                  />
                </div>
                <span className="text-sm font-mono font-bold text-white w-12 text-right">
                  {call.mlScore.toFixed(2)}
                </span>
              </div>
            </div>

            {/* Reason text */}
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">{call.reason}</p>
          </div>
        ))}
      </div>
    </Card>
  )
}
