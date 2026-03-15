import { BarChart3 } from 'lucide-react'
import { useModelInfo, useCoverageStats, useEmployeePerformance } from '../hooks/api'
import { ModelMetricsHero } from '../components/analytics/ModelMetricsHero'
import { FeatureImportanceChart } from '../components/analytics/FeatureImportanceChart'
import { CoverageMetrics } from '../components/analytics/CoverageMetrics'
import { EmployeeLeaderboard } from '../components/analytics/EmployeeLeaderboard'

export default function Analytics() {
  const modelInfoQuery = useModelInfo()
  const coverageQuery = useCoverageStats()
  const performanceQuery = useEmployeePerformance()

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <BarChart3 className="w-6 h-6 text-cyan-400" />
        <div>
          <h1 className="text-2xl font-bold text-white">Analytics</h1>
          <p className="text-slate-400 text-sm mt-0.5">
            ML model performance, coverage statistics, and employee leaderboard
          </p>
        </div>
      </div>

      {/* Hero model metrics */}
      <ModelMetricsHero
        modelInfo={modelInfoQuery.data}
        isLoading={modelInfoQuery.isLoading}
      />

      {/* Coverage metrics */}
      <CoverageMetrics
        stats={coverageQuery.data}
        isLoading={coverageQuery.isLoading}
      />

      {/* Two-column: Feature importance + Leaderboard */}
      <div className="grid grid-cols-5 gap-4">
        <div className="col-span-3">
          <FeatureImportanceChart
            featureImportances={modelInfoQuery.data?.feature_importances}
            isLoading={modelInfoQuery.isLoading}
          />
        </div>
        <div className="col-span-2">
          <EmployeeLeaderboard
            employees={performanceQuery.data}
            isLoading={performanceQuery.isLoading}
          />
        </div>
      </div>
    </div>
  )
}
