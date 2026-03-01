import { AlertTriangle } from 'lucide-react'
import { Button } from './Button'

interface ErrorCardProps {
  title?: string
  message: string
  onRetry?: () => void
}

export function ErrorCard({
  title = 'Something went wrong',
  message,
  onRetry,
}: ErrorCardProps) {
  return (
    <div className="bg-slate-800/50 border border-rose-500/30 rounded-xl p-6">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <h3 className="text-sm font-medium text-rose-300">{title}</h3>
          <p className="text-sm text-slate-400">{message}</p>
        </div>
      </div>
      {onRetry && (
        <div className="mt-4">
          <Button variant="secondary" size="sm" onClick={onRetry}>
            Retry
          </Button>
        </div>
      )}
    </div>
  )
}
