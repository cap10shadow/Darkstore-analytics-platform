import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Legend, CartesianGrid } from 'recharts'
import { COLORS } from './chartTheme'
import type { CompareResponse } from '../../types/forecast'

interface ModelComparisonBarProps {
  comparison: CompareResponse
}

export default function ModelComparisonBar({ comparison }: ModelComparisonBarProps) {
  const data = Object.entries(comparison.models).map(([name, metrics]) => ({
    name,
    MAE: Math.round(metrics.mae * 100) / 100,
    RMSE: Math.round(metrics.rmse * 100) / 100,
    MAPE: Math.round(metrics.mape * 100) / 100,
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a3650" />
        <XAxis
          dataKey="name"
          tick={{ fill: '#94a3b8', fontSize: 11 }}
          axisLine={{ stroke: '#2a3650' }}
          tickLine={false}
          angle={-30}
          textAnchor="end"
          height={60}
        />
        <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip
          contentStyle={{ backgroundColor: '#1a2236', border: '1px solid #2a3650', borderRadius: '8px', color: '#f1f5f9' }}
        />
        <Legend formatter={(v) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{v}</span>} />
        <Bar dataKey="MAE" fill={COLORS.cyan} radius={[3, 3, 0, 0]} />
        <Bar dataKey="RMSE" fill={COLORS.violet} radius={[3, 3, 0, 0]} />
        <Bar dataKey="MAPE" fill={COLORS.amber} radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
