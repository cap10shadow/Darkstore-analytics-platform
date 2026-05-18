const severityColors: Record<string, string> = {
  critical: 'bg-rose-500/15 text-rose-400',
  high: 'bg-amber-500/15 text-amber-400',
  medium: 'bg-yellow-500/15 text-yellow-400',
  low: 'bg-blue-500/15 text-blue-400',
  info: 'bg-cyan-500/15 text-cyan-400',
}

export default function SeverityBadge({ severity }: { severity: string }) {
  const color = severityColors[severity.toLowerCase()] || 'bg-navy-700 text-text-secondary'
  return (
    <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${color}`}>
      {severity}
    </span>
  )
}
