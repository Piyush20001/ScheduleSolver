import { useEffect, useRef } from 'react'
import { Phone, CheckCircle, XCircle, PhoneOff, Voicemail, PhoneCall, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Card } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { ScoreBar } from '../common/ScoreBar'
import type { CallAttempt, DemoState } from '../../hooks/useDemoFlow'

interface CallTimelineProps {
  calls: CallAttempt[]
  demoStatus: DemoState['status']
}

function CallStatusIndicator({ status }: { status: CallAttempt['status'] }) {
  switch (status) {
    case 'ringing':
      return (
        <motion.div
          className="flex items-center gap-2 text-cyan-400"
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <Phone className="w-3 h-3" />
          <span className="text-xs">Ringing...</span>
        </motion.div>
      )
    case 'accepted':
      return (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 text-emerald-400"
        >
          <CheckCircle className="w-3 h-3" />
          <span className="text-xs font-medium">Accepted</span>
        </motion.div>
      )
    case 'declined':
      return (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 text-rose-400"
        >
          <XCircle className="w-3 h-3" />
          <span className="text-xs font-medium">Declined</span>
        </motion.div>
      )
    case 'no_answer':
      return (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 text-slate-400"
        >
          <PhoneOff className="w-3 h-3" />
          <span className="text-xs font-medium">No Answer</span>
        </motion.div>
      )
    case 'voicemail':
      return (
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-2 text-amber-400"
        >
          <Voicemail className="w-3 h-3" />
          <span className="text-xs font-medium">Voicemail</span>
        </motion.div>
      )
  }
}

function getCallBorderStyle(status: CallAttempt['status']): string {
  switch (status) {
    case 'ringing':
      return 'bg-cyan-500/5 border-cyan-500/30 shadow-[0_0_15px_rgba(34,211,238,0.15)]'
    case 'accepted':
      return 'bg-emerald-500/5 border-emerald-500/30'
    case 'declined':
      return 'bg-rose-500/5 border-rose-500/30'
    case 'no_answer':
      return 'bg-slate-600/5 border-slate-600/30'
    case 'voicemail':
      return 'bg-amber-500/5 border-amber-500/30'
  }
}

export function CallTimeline({ calls, demoStatus }: CallTimelineProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    })
  }, [calls.length])

  return (
    <Card>
      <div className="flex items-center gap-2 mb-4">
        <PhoneCall className="w-5 h-5 text-cyan-400" />
        <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
          Call Timeline
        </h3>
      </div>

      <div ref={scrollRef} className="max-h-[500px] overflow-y-auto space-y-3">
        {demoStatus === 'idle' && calls.length === 0 && (
          <div className="flex items-center justify-center py-12 text-center">
            <p className="text-sm text-slate-500">Start a demo to see live call activity</p>
          </div>
        )}

        {demoStatus === 'creating' && (
          <div className="flex items-center justify-center gap-2 py-8">
            <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
            <span className="text-sm text-slate-400">Creating incident...</span>
          </div>
        )}

        <AnimatePresence>
          {calls.map((call, index) => (
            <motion.div
              key={call.callOrder}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              className="relative"
            >
              {/* Timeline connector line */}
              {index > 0 && (
                <div className="absolute left-4 -top-3 w-0.5 h-3 bg-slate-700" />
              )}

              <div
                className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${getCallBorderStyle(call.status)}`}
              >
                {/* Call order badge */}
                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold text-white flex-shrink-0">
                  {call.callOrder}
                </div>

                <div className="flex-1 min-w-0">
                  {/* Candidate info */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-white">{call.name}</span>
                    <Badge>{call.role}</Badge>
                  </div>

                  {/* ML Score bar */}
                  <div className="mt-1">
                    <ScoreBar score={call.mlScore} height="h-1.5" />
                  </div>

                  {/* Status indicator */}
                  <div className="mt-2">
                    <CallStatusIndicator status={call.status} />
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Resolution banner */}
        {demoStatus === 'escalated' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-center"
          >
            <p className="text-sm text-rose-400">
              All candidates exhausted &mdash; manual intervention needed
            </p>
          </motion.div>
        )}
      </div>
    </Card>
  )
}
