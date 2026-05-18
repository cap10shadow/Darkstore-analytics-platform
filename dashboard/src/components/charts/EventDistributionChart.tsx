import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell, CartesianGrid } from 'recharts'
import { COLORS } from './chartTheme'

interface EventDistributionChartProps {
  eventCounts: Record<string, number>
}

const eventColors: Record<string, string> = {
  order_placed: COLORS.cyan,
  order_picked: COLORS.blue,
  order_packed: COLORS.violet,
  order_delivered: COLORS.emerald,
  stock_alert: COLORS.amber,
  anomaly_detected: COLORS.rose,
}

export default function EventDistributionChart({ eventCounts }: EventDistributionChartProps) {
  const data = Object.entries(eventCounts)
    .map(([type, count]) => ({ type: type.replace(/_/g, ' '), count, raw: type }))
    .sort((a, b) => b.count - a.count)

  const fallbackColors = Object.values(COLORS)

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a3650" />
        <XAxis
          dataKey="type"
          tick={{ fill: '#94a3b8', fontSize: 11 }}
          axisLine={{ stroke: '#2a3650' }}
          tickLine={false}
          angle={-25}
          textAnchor="end"
          height={60}
        />
        <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip
          contentStyle={{ backgroundColor: '#1a2236', border: '1px solid #2a3650', borderRadius: '8px', color: '#f1f5f9' }}
        />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((entry, i) => (
            <Cell key={entry.raw} fill={eventColors[entry.raw] || fallbackColors[i % fallbackColors.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
