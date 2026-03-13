import { Zap, Loader2, CheckCircle, AlertTriangle } from 'lucide-react'
import { motion } from 'framer-motion'
import type { DemoState } from '../../hooks/useDemoFlow'

interface TriggerDemoButtonProps {
  onTrigger: () => void
  onReset: () => void
  status: DemoState['status']
  error: string | null
}

export function TriggerDemoButton({
  onTrigger,
  onReset,
  status,
  error,
}: TriggerDemoButtonProps) {
  if (error) {
    return (
      <div className="flex items-center gap-3">
        <div className="px-4 py-2 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm">
          <AlertTriangle className="w-4 h-4 inline mr-1" />
          {error}
        </div>
        <button
          onClick={onTrigger}
          className="text-sm text-slate-400 hover:text-white transition-colors"
        >
          Retry
        </button>
      </div>
    )
  }

  switch (status) {
    case 'idle':
      return (
        <motion.button
          onClick={onTrigger}
          className="px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-cyan-500 to-cyan-400 hover:from-cyan-400 hover:to-cyan-300 shadow-lg shadow-cyan-500/25 transition-all"
          animate={{ scale: [1, 1.02, 1] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        >
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            <span>Trigger Demo</span>
          </div>
        </motion.button>
      )

    case 'creating':
      return (
        <button
          disabled
          className="px-6 py-3 rounded-xl font-semibold text-white/70 bg-cyan-500/30 cursor-not-allowed"
        >
          <div className="flex items-center gap-2">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Creating Incident...</span>
          </div>
        </button>
      )

    case 'calling':
      return (
        <button
          disabled
          className="px-6 py-3 rounded-xl font-semibold text-cyan-400 bg-cyan-500/10 border border-cyan-500/30 cursor-not-allowed"
        >
          <div className="flex items-center gap-2">
            <motion.div
              className="w-2 h-2 rounded-full bg-cyan-400"
              animate={{ opacity: [1, 0.3, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
            <span>Demo Running...</span>
          </div>
        </button>
      )

    case 'resolved':
      return (
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm font-medium">
            <CheckCircle className="w-4 h-4 inline mr-1" />
            Resolved!
          </div>
          <button
            onClick={onReset}
            className="text-sm text-slate-400 hover:text-white transition-colors"
          >
            Run Again
          </button>
        </div>
      )

    case 'escalated':
      return (
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 text-sm font-medium">
            <AlertTriangle className="w-4 h-4 inline mr-1" />
            Escalated
          </div>
          <button
            onClick={onReset}
            className="text-sm text-slate-400 hover:text-white transition-colors"
          >
            Run Again
          </button>
        </div>
      )
  }
}
