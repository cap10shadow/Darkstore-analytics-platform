import { Database } from 'lucide-react'

export default function TopBar() {
  return (
    <header className="h-14 bg-navy-800 border-b border-navy-700 flex items-center justify-between px-6 sticky top-0 z-20">
      <div />
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-sm text-text-secondary">
          <Database className="h-4 w-4" />
          <span>Demo data</span>
        </div>
      </div>
    </header>
  )
}
