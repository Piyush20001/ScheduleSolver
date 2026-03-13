import { Radio, CheckCircle } from 'lucide-react'
import { motion } from 'framer-motion'
import { useDemoFlow } from '../hooks/useDemoFlow'
import { ErrorCard } from '../components/ui/ErrorCard'
import {
  ActiveIncidents,
  CallTimeline,
  CandidateRanking,
  EventFeed,
  TriggerDemoButton,
} from '../components/command-center'

export default function CommandCenter() {
  const { state, triggerDemo, reset } = useDemoFlow()

  return (
    <div className="space-y-4">
      {/* Page header with Trigger Demo button */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Radio className="w-6 h-6 text-cyan-400" />
          <h1 className="text-2xl font-bold text-white">Command Center</h1>
        </div>
        <TriggerDemoButton
          onTrigger={triggerDemo}
          onReset={reset}
          status={state.status}
          error={state.error}
        />
      </div>

      {/* Error state */}
      {state.error && (
        <ErrorCard message={state.error} onRetry={triggerDemo} />
      )}

      {/* Resolution success banner */}
      {state.status === 'resolved' && state.resolution && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-3"
        >
          <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          <span className="text-sm text-emerald-300">
            Incident resolved! {state.resolution.replacementName} (
            {state.resolution.replacementRole}) accepted after{' '}
            {state.resolution.totalCalls} call(s).
          </span>
        </motion.div>
      )}

      {/* 3-column layout */}
      <div className="grid grid-cols-12 gap-4">
        {/* Left: Active Incidents (3 cols) */}
        <div className="col-span-3">
          <ActiveIncidents activeIncidentId={state.incidentId} />
        </div>

        {/* Center: Call Timeline (5 cols) */}
        <div className="col-span-5">
          <CallTimeline calls={state.calls} demoStatus={state.status} />
        </div>

        {/* Right: Candidate Ranking (4 cols) */}
        <div className="col-span-4">
          <CandidateRanking calls={state.calls} demoStatus={state.status} />
        </div>
      </div>

      {/* Event Feed (collapsible, full width below) */}
      <EventFeed events={state.events} />
    </div>
  )
}
