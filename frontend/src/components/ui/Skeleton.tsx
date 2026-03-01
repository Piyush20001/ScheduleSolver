interface SkeletonLineProps {
  width?: string
  height?: string
  className?: string
}

export function SkeletonLine({
  width = 'w-full',
  height = 'h-4',
  className = '',
}: SkeletonLineProps) {
  return (
    <div
      className={`rounded bg-slate-700/50 animate-skeleton ${width} ${height} ${className}`}
    />
  )
}

interface SkeletonCardProps {
  className?: string
}

export function SkeletonCard({ className = '' }: SkeletonCardProps) {
  return (
    <div
      className={`bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 space-y-3 ${className}`}
    >
      <SkeletonLine width="w-1/3" height="h-5" />
      <SkeletonLine width="w-full" />
      <SkeletonLine width="w-2/3" />
    </div>
  )
}

interface SkeletonTableProps {
  rows?: number
  columns?: number
  className?: string
}

export function SkeletonTable({
  rows = 5,
  columns = 4,
  className = '',
}: SkeletonTableProps) {
  return (
    <div
      className={`bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="flex gap-4 p-4 border-b border-slate-700/50">
        {Array.from({ length: columns }).map((_, i) => (
          <SkeletonLine key={`header-${i}`} width="flex-1" height="h-4" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div
          key={`row-${rowIndex}`}
          className="flex gap-4 p-4 border-b border-slate-700/30 last:border-b-0"
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <SkeletonLine key={`cell-${rowIndex}-${colIndex}`} width="flex-1" height="h-3" />
          ))}
        </div>
      ))}
    </div>
  )
}
