export interface RouteOptimizeRequest {
  pick_list: string[]
  method?: string
}

export interface RouteOptimizeResponse {
  route: string[]
  coordinates: [number, number][]
  distance: number
  naive_distance: number
  estimated_time_minutes: number
  improvement_percent: number
  num_stops: number
}
