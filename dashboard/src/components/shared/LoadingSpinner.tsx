import { Loader2 } from 'lucide-react'

export default function LoadingSpinner({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-text-secondary">
      <Loader2 className="h-8 w-8 animate-spin text-accent-cyan mb-3" />
      <p className="text-sm">{message}</p>
    </div>
  )
}
