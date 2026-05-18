const healthColors: Record<string, string> = {
  healthy: 'bg-emerald-500/15 text-emerald-400',
  low: 'bg-amber-500/15 text-amber-400',
  critical: 'bg-rose-500/15 text-rose-400',
}

export default function HealthBadge({ status }: { status: string }) {
  const color = healthColors[status.toLowerCase()] || 'bg-navy-700 text-text-secondary'
  return (
    <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${color}`}>
      {status}
    </span>
  )
}
