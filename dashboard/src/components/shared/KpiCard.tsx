import type { ReactNode } from 'react'

interface KpiCardProps {
  label: string
  value: string | number
  icon: ReactNode
  color: string
  subtitle?: string
}

export default function KpiCard({ label, value, icon, color, subtitle }: KpiCardProps) {
  return (
    <div className="bg-navy-800 border border-navy-700 rounded-xl p-5 flex items-start gap-4">
      <div className={`p-3 rounded-lg ${color}`}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-text-secondary text-sm truncate">{label}</p>
        <p className="text-2xl font-bold text-text-primary mt-0.5">{value}</p>
        {subtitle && <p className="text-text-secondary text-xs mt-1">{subtitle}</p>}
      </div>
    </div>
  )
}
