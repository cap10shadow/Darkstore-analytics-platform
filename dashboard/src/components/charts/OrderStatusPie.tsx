import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { STATUS_COLORS, COLORS } from './chartTheme'
import type { Order } from '../../types/data'

interface OrderStatusPieProps {
  orders: Order[]
}

export default function OrderStatusPie({ orders }: OrderStatusPieProps) {
  const counts: Record<string, number> = {}
  orders.forEach((o) => {
    const s = o.status
    counts[s] = (counts[s] || 0) + 1
  })
  const data = Object.entries(counts).map(([name, value]) => ({ name, value }))

  const fallbackColors = [COLORS.cyan, COLORS.emerald, COLORS.violet, COLORS.amber, COLORS.rose, COLORS.blue]

  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={3}
          dataKey="value"
          stroke="none"
        >
          {data.map((entry, i) => (
            <Cell key={entry.name} fill={STATUS_COLORS[entry.name] || fallbackColors[i % fallbackColors.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ backgroundColor: '#1a2236', border: '1px solid #2a3650', borderRadius: '8px', color: '#f1f5f9' }}
          itemStyle={{ color: '#f1f5f9' }}
        />
        <Legend
          formatter={(value) => <span style={{ color: '#94a3b8', fontSize: '12px' }}>{value}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}
