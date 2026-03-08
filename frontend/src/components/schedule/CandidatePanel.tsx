import { useEffect } from 'react'
import { X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Badge } from '../ui/Badge'
import { SkeletonCard } from '../ui/Skeleton'
import { EmptyState } from '../ui/EmptyState'
import { ScoreBar } from '../common/ScoreBar'
import { useRankCandidates } from '../../hooks/api'
import type { ShiftEnriched } from '../../types'

interface CandidatePanelProps {
  shift: ShiftEnriched | null
  onClose: () => void
}

export function CandidatePanel({ shift, onClose }: CandidatePanelProps) {
  const rankMutation = useRankCandidates()

  useEffect(() => {
    if (shift) {
      rankMutation.mutate({ shift_id: shift.id })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [shift?.id])

  return (
    <AnimatePresence>
      {shift && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/40 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          {/* Panel */}
          <motion.div
            className="fixed right-0 top-0 h-full w-96 bg-slate-900 border-l border-slate-700 z-50 overflow-y-auto p-6"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-white">ML-Ranked Candidates</h3>
                <p className="text-sm text-slate-400 mt-1">
                  {shift.date} &middot; {shift.start_time}-{shift.end_time} &middot;{' '}
                  <span className="capitalize">{shift.role_required}</span>
                </p>
              </div>
              <button
                onClick={onClose}
                className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Loading */}
            {rankMutation.isPending && (
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, i) => (
                  <SkeletonCard key={i} />
                ))}
              </div>
            )}

            {/* Error */}
            {rankMutation.isError && (
              <p className="text-sm text-rose-400">Failed to load candidates</p>
            )}

            {/* Results */}
            {rankMutation.isSuccess && rankMutation.data.candidates.length === 0 && (
              <EmptyState title="No candidates available" />
            )}

            {rankMutation.isSuccess && rankMutation.data.candidates.length > 0 && (
              <div className="space-y-3">
                {rankMutation.data.candidates.map((candidate) => (
                  <div
                    key={candidate.employee_id}
                    className="flex flex-col gap-1 p-3 rounded-lg bg-slate-800/50 border border-slate-700/50"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-white">{candidate.name}</span>
                      <Badge>{candidate.role}</Badge>
                    </div>
                    <ScoreBar score={candidate.score} height="h-3" />
                    <p className="text-xs text-slate-400 mt-1">{candidate.reason}</p>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
