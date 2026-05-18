import { post } from './client'
import type { RouteOptimizeRequest, RouteOptimizeResponse } from '../types/routes'

export const optimizeRoute = (req: RouteOptimizeRequest) =>
  post<RouteOptimizeResponse>('/api/v1/routes/optimize', req)
