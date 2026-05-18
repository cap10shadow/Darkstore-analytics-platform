export interface AffinityPair {
  sku_a: string
  product_a: string
  category_a: string
  location_a: string
  sku_b: string
  product_b: string
  category_b: string
  location_b: string
  co_occurrences: number
  confidence_a_to_b: number
  lift: number
  affinity_score: number
}

export interface AffinityPairsResponse {
  pairs: AffinityPair[]
  total: number
}

export interface ColocationRecommendation {
  sku_a: string
  sku_b: string
  product_a: string
  product_b: string
  current_distance: number
  co_occurrences_weekly: number
  affinity_score: number
  lift: number
  estimated_annual_time_saved_hours: number
  recommendation: string
  priority: string
}

export interface ColocationResponse {
  recommendations: ColocationRecommendation[]
  total: number
}
