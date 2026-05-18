import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from 'recharts'
import type { ForecastResponse } from '../../types/forecast'

interface ForecastLineChartProps {
  forecast: ForecastResponse
}

export default function ForecastLineChart({ forecast }: ForecastLineChartProps) {
  if (!forecast.has_data || !forecast.historical_dates || !forecast.forecast_dates) {
    return <p className="text-text-secondary text-center py-10">No forecast data available</p>
  }

  const histData = forecast.historical_dates.map((date, i) => ({
    date,
    historical: forecast.historical_demand?.[i] ?? null,
    forecast: null as number | null,
    lower: null as number | null,
    upper: null as number | null,
  }))

  const foreData = forecast.forecast_dates.map((date, i) => ({
    date,
    historical: null as number | null,
    forecast: forecast.forecast?.[i] ?? null,
    lower: forecast.lower_ci?.[i] ?? null,
    upper: forecast.upper_ci?.[i] ?? null,
  }))

  // Connect historical and forecast by duplicating last historical point
  if (histData.length > 0 && foreData.length > 0) {
    const lastHist = histData[histData.length - 1]
    foreData[0] = {
      ...foreData[0],
      historical: lastHist.historical,
    }
  }

  const allData = [...histData, ...foreData]
  const todayDate = forecast.historical_dates[forecast.historical_dates.length - 1]

  const formatDate = (d: string) => {
    const parts = d.split('-')
    return `${parts[1]}/${parts[2]}`
  }

  return (
    <ResponsiveContainer width="100%" height={350}>
      <ComposedChart data={allData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a3650" />
        <XAxis
          dataKey="date"
          tick={{ fill: '#94a3b8', fontSize: 11 }}
          axisLine={{ stroke: '#2a3650' }}
          tickLine={false}
          tickFormatter={formatDate}
          interval="preserveStartEnd"
        />
        <YAxis
          tick={{ fill: '#94a3b8', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{ backgroundColor: '#1a2236', border: '1px solid #2a3650', borderRadius: '8px', color: '#f1f5f9' }}
          labelFormatter={(l) => `Date: ${l}`}
        />
        <Area
          dataKey="upper"
          stroke="none"
          fill="#8b5cf6"
          fillOpacity={0.1}
          connectNulls={false}
        />
        <Area
          dataKey="lower"
          stroke="none"
          fill="#0f1729"
          fillOpacity={1}
          connectNulls={false}
        />
        <Line
          dataKey="historical"
          stroke="#06b6d4"
          strokeWidth={2}
          dot={false}
          connectNulls={false}
          name="Historical"
        />
        <Line
          dataKey="forecast"
          stroke="#8b5cf6"
          strokeWidth={2}
          strokeDasharray="6 3"
          dot={false}
          connectNulls={false}
          name="Forecast"
        />
        {todayDate && (
          <ReferenceLine
            x={todayDate}
            stroke="#f59e0b"
            strokeDasharray="4 4"
            label={{ value: 'Today', position: 'top', fill: '#f59e0b', fontSize: 11 }}
          />
        )}
      </ComposedChart>
    </ResponsiveContainer>
  )
}
