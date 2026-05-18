import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts'
import { SEVERITY_COLORS } from './chartTheme'
import type { Alert } from '../../types/data'

interface AlertsSummaryChartProps {
  alerts: Alert[]
}

export default function AlertsSummaryChart({ alerts }: AlertsSummaryChartProps) {
  const counts: Record<string, number> = {}
  alerts.forEach((a) => {
    const s = a.severity.toLowerCase()
    counts[s] = (counts[s] || 0) + 1
  })
  const data = Object.entries(counts)
    .map(([severity, count]) => ({ severity, count }))
    .sort((a, b) => {
      const order = ['critical', 'high', 'medium', 'low', 'info']
      return order.indexOf(a.severity) - order.indexOf(b.severity)
    })

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
        <XAxis
          dataKey="severity"
          tick={{ fill: '#94a3b8', fontSize: 12 }}
          axisLine={{ stroke: '#2a3650' }}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: '#94a3b8', fontSize: 12 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{ backgroundColor: '#1a2236', border: '1px solid #2a3650', borderRadius: '8px', color: '#f1f5f9' }}
        />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((entry) => (
            <Cell key={entry.severity} fill={SEVERITY_COLORS[entry.severity] || '#3b82f6'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
