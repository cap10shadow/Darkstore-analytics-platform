import { get } from './client'
import type { AffinityPairsResponse, ColocationResponse } from '../types/affinity'

export const fetchAffinityPairs = (topN = 20, minLift = 1.0) =>
  get<AffinityPairsResponse>(`/api/v1/affinity/pairs?top_n=${topN}&min_lift=${minLift}`)

export const fetchRecommendations = (distanceThreshold = 50) =>
  get<ColocationResponse>(`/api/v1/affinity/recommendations?distance_threshold=${distanceThreshold}`)
