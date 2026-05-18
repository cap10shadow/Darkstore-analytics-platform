import { AlertTriangle, RefreshCw } from 'lucide-react'

interface ErrorCardProps {
  message: string
  onRetry?: () => void
}

export default function ErrorCard({ message, onRetry }: ErrorCardProps) {
  return (
    <div className="bg-navy-800 border border-accent-rose/30 rounded-xl p-6 text-center">
      <AlertTriangle className="h-8 w-8 text-accent-rose mx-auto mb-3" />
      <p className="text-text-primary font-medium mb-1">Something went wrong</p>
      <p className="text-text-secondary text-sm mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-accent-rose/10 text-accent-rose hover:bg-accent-rose/20 transition-colors text-sm"
        >
          <RefreshCw className="h-4 w-4" />
          Retry
        </button>
      )}
    </div>
  )
}
