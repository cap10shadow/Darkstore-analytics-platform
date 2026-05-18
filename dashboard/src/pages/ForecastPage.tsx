import { useState, useCallback } from 'react'
import { TrendingUp, TrendingDown, Minus, AlertCircle, BarChart3 } from 'lucide-react'
import { useApi } from '../hooks/useApi'
import { useMutation } from '../hooks/useMutation'
import { fetchInventory } from '../api/data'
import { forecastSku, compareModels } from '../api/forecast'
import PageHeader from '../components/shared/PageHeader'
import Card from '../components/shared/Card'
import ErrorCard from '../components/shared/ErrorCard'
import ForecastLineChart from '../components/charts/ForecastLineChart'
import ModelComparisonBar from '../components/charts/ModelComparisonBar'
import type { ForecastRequest } from '../types/forecast'
import type { CompareRequest } from '../types/forecast'

const MODELS = ['auto', 'ensemble', 'arima', 'sarima', 'holt_winters', 'rf', 'gbm', 'xgboost', 'lightgbm', 'prophet']

export default function ForecastPage() {
  const { data: invData, loading: invLoading } = useApi(() => fetchInventory(1000))
  const [skuId, setSkuId] = useState('')
  const [forecastDays, setForecastDays] = useState(14)
  const [model, setModel] = useState('auto')

  const forecastMutation = useMutation(
    useCallback((req: ForecastRequest) => forecastSku(req), [])
  )
  const compareMutation = useMutation(
    useCallback((req: CompareRequest) => compareModels(req), [])
  )

  const handleForecast = () => {
    if (!skuId) return
    forecastMutation.execute({ sku_id: skuId, forecast_days: forecastDays, mode: model })
  }

  const handleCompare = () => {
    if (!skuId) return
    compareMutation.execute({ sku_id: skuId, forecast_days: forecastDays })
  }

  const skus = invData?.items?.map((i) => i.sku_id) ?? []
  const forecast = forecastMutation.data
  const comparison = compareMutation.data

  const TrendIcon = forecast?.trend === 'increasing' ? TrendingUp : forecast?.trend === 'decreasing' ? TrendingDown : Minus

  return (
    <div>
      <PageHeader title="Demand Forecasting" description="Predict future demand per SKU using ML models" />

      {/* Controls */}
      <Card className="mb-6">
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs text-text-secondary mb-1">SKU</label>
            {invLoading ? (
              <div className="bg-navy-900 border border-navy-700 rounded-lg px-3 py-2 text-sm text-text-secondary">Loading SKUs...</div>
            ) : (
              <select
                value={skuId}
                onChange={(e) => setSkuId(e.target.value)}
                className="w-full bg-navy-900 border border-navy-700 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
              >
                <option value="">Select SKU...</option>
                {skus.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            )}
          </div>
          <div className="w-48">
            <label className="block text-xs text-text-secondary mb-1">Forecast Days: {forecastDays}</label>
            <input
              type="range"
              min={7}
              max={90}
              value={forecastDays}
              onChange={(e) => setForecastDays(Number(e.target.value))}
              className="w-full accent-accent-cyan"
            />
          </div>
          <div className="w-40">
            <label className="block text-xs text-text-secondary mb-1">Model</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full bg-navy-900 border border-navy-700 rounded-lg px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent-cyan"
            >
              {MODELS.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
          <button
            onClick={handleForecast}
            disabled={!skuId || forecastMutation.loading}
            className="px-4 py-2 rounded-lg bg-accent-cyan text-navy-900 font-medium text-sm hover:bg-accent-cyan/80 disabled:opacity-40 transition-colors"
          >
            {forecastMutation.loading ? 'Forecasting...' : 'Run Forecast'}
          </button>
          <button
            onClick={handleCompare}
            disabled={!skuId || compareMutation.loading}
            className="px-4 py-2 rounded-lg bg-accent-violet text-white font-medium text-sm hover:bg-accent-violet/80 disabled:opacity-40 transition-colors flex items-center gap-2"
          >
            <BarChart3 className="h-4 w-4" />
            {compareMutation.loading ? 'Comparing...' : 'Compare Models'}
          </button>
        </div>
      </Card>

      {forecastMutation.error && <ErrorCard message={forecastMutation.error} />}

      {/* Forecast Chart */}
      {forecast && (
        <>
          <Card className="mb-6">
            <h3 className="text-sm font-semibold text-text-primary mb-4">
              Demand Forecast - {forecast.sku_id}
              {forecast.product_name && <span className="text-text-secondary font-normal ml-2">({forecast.product_name})</span>}
            </h3>
            <ForecastLineChart forecast={forecast} />
          </Card>

          {/* Info Cards */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <Card>
              <p className="text-xs text-text-secondary mb-1">Model Used</p>
              <p className="text-lg font-semibold text-accent-cyan">{forecast.model_used}</p>
            </Card>
            <Card>
              <p className="text-xs text-text-secondary mb-1">Trend</p>
              <p className="text-lg font-semibold text-text-primary flex items-center gap-2">
                <TrendIcon className={`h-5 w-5 ${forecast.trend === 'increasing' ? 'text-accent-emerald' : forecast.trend === 'decreasing' ? 'text-accent-rose' : 'text-text-secondary'}`} />
                {forecast.trend}
              </p>
            </Card>
            <Card>
              <p className="text-xs text-text-secondary mb-1">Total Forecast Demand</p>
              <p className="text-lg font-semibold text-text-primary">{forecast.total_forecast_demand?.toFixed(0) ?? '--'}</p>
            </Card>
            <Card>
              <p className="text-xs text-text-secondary mb-1">Needs Reorder</p>
              <p className={`text-lg font-semibold flex items-center gap-2 ${forecast.needs_reorder ? 'text-accent-rose' : 'text-accent-emerald'}`}>
                {forecast.needs_reorder ? <><AlertCircle className="h-5 w-5" /> Yes</> : 'No'}
              </p>
            </Card>
          </div>
        </>
      )}

      {/* Model Comparison */}
      {compareMutation.error && <ErrorCard message={compareMutation.error} />}
      {comparison && !comparison.error && (
        <Card>
          <h3 className="text-sm font-semibold text-text-primary mb-4">Model Comparison - {comparison.sku_id}</h3>
          {comparison.data_warning && (
            <p className="text-xs text-accent-amber mb-3">{comparison.data_warning}</p>
          )}
          <ModelComparisonBar comparison={comparison} />
        </Card>
      )}
    </div>
  )
}
