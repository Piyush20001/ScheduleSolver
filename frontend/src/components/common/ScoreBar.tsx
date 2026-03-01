interface ScoreBarProps {
  score: number
  showLabel?: boolean
  height?: string
  className?: string
}

export function ScoreBar({
  score,
  showLabel = true,
  height = 'h-2',
  className,
}: ScoreBarProps) {
  const percentage = Math.round(score * 100)
  const color =
    score >= 0.8
      ? 'bg-emerald-500'
      : score >= 0.5
        ? 'bg-amber-500'
        : 'bg-rose-500'

  return (
    <div className={`flex items-center gap-2 ${className ?? ''}`}>
      <div className={`flex-1 ${height} bg-slate-700 rounded-full overflow-hidden`}>
        <div
          className={`${height} ${color} rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-xs text-slate-400 w-10 text-right font-mono">
          {score.toFixed(2)}
        </span>
      )}
    </div>
  )
}
