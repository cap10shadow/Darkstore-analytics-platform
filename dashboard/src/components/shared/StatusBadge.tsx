const statusColors: Record<string, string> = {
  pending: 'bg-amber-500/15 text-amber-400',
  picking: 'bg-blue-500/15 text-blue-400',
  packing: 'bg-violet-500/15 text-violet-400',
  packed: 'bg-violet-500/15 text-violet-400',
  delivered: 'bg-emerald-500/15 text-emerald-400',
  shipped: 'bg-cyan-500/15 text-cyan-400',
  cancelled: 'bg-rose-500/15 text-rose-400',
}

export default function StatusBadge({ status }: { status: string }) {
  const color = statusColors[status.toLowerCase()] || 'bg-navy-700 text-text-secondary'
  return (
    <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${color}`}>
      {status}
    </span>
  )
}
