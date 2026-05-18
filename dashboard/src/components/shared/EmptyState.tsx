import { Inbox } from 'lucide-react'

interface EmptyStateProps {
  title?: string
  message?: string
}

export default function EmptyState({ title = 'No data', message = 'No results found.' }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-text-secondary">
      <Inbox className="h-10 w-10 mb-3 opacity-50" />
      <p className="font-medium text-text-primary">{title}</p>
      <p className="text-sm">{message}</p>
    </div>
  )
}
