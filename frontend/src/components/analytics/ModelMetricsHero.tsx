import { Brain } from 'lucide-react'
import { Card } from '../ui/Card'
import { SkeletonCard } from '../ui/Skeleton'
import type { ModelInfo } from '../../types'

interface ModelMetricsHeroProps {
  modelInfo: ModelInfo | undefined
  isLoading: boolean
}

function MetricItem({ label, value }: { label: string; value?: number }) {
  return (
    <div className="text-center">
      <p className="text-2xl font-semibold text-white font-mono">
        {value !== undefined ? (value * 100).toFixed(1) + '%' : '---'}
      </p>
      <p className="text-xs text-slate-400 mt-1">{label}</p>
    </div>
  )
}

export function ModelMetricsHero({ modelInfo, isLoading }: ModelMetricsHeroProps) {
  if (isLoading) {
    return <SkeletonCard className="h-[240px]" />
  }

  return (
    <Card className="relative overflow-hidden">
      <div className="flex items-center gap-2 mb-4">
        <Brain className="w-5 h-5 text-cyan-400" />
        <h3 className="text-sm font-medium text-slate-400 uppercase tracking-wider">
          ML Model Performance
        </h3>
      </div>

      {/* Hero ROC-AUC */}
      <div className="text-center py-4">
        <p className="text-6xl font-bold text-white font-mono tracking-tight">
          {modelInfo?.roc_auc.toFixed(3) ?? '---'}
        </p>
        <p className="text-sm text-cyan-400 mt-2">ROC-AUC Score</p>
      </div>

      {/* Secondary metrics row */}
      <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-700/50">
        <MetricItem label="Accuracy" value={modelInfo?.accuracy} />
        <MetricItem label="Precision" value={modelInfo?.precision} />
        <MetricItem label="Recall" value={modelInfo?.recall} />
      </div>
    </Card>
  )
}
