export interface ForecastRequest {
  sku_id: string
  forecast_days?: number
  mode?: string
}

export interface ForecastResponse {
  sku_id: string
  has_data: boolean
  message?: string
  model_used?: string
  historical_days?: number
  historical_demand?: number[]
  historical_dates?: string[]
  forecast_days?: number
  forecast?: number[]
  lower_ci?: number[]
  upper_ci?: number[]
  forecast_dates?: string[]
  avg_historical_daily?: number
  avg_forecast_daily?: number
  trend?: string
  total_forecast_demand?: number
  all_models?: string[]
  product_name?: string
  category?: string
  current_stock?: number
  reorder_threshold?: number
  needs_reorder?: boolean
}

export interface CompareRequest {
  sku_id: string
  forecast_days?: number
}

export interface ModelMetrics {
  forecast: number[]
  mape: number
  rmse: number
  mae: number
  [key: string]: unknown
}

export interface CompareResponse {
  sku_id: string
  models: Record<string, ModelMetrics>
  data_length: number
  data_warning?: string
  error?: string
}
