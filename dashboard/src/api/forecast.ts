import { post } from './client'
import type { ForecastRequest, ForecastResponse, CompareRequest, CompareResponse } from '../types/forecast'

export const forecastSku = (req: ForecastRequest) =>
  post<ForecastResponse>('/api/v1/forecast/sku', req)

export const compareModels = (req: CompareRequest) =>
  post<CompareResponse>('/api/v1/forecast/compare', req)
