export interface SimulationRequest {
  scenario_type: 'normal' | 'flash_sale' | 'supply_delay'
  duration_hours?: number
  orders_per_hour?: number
  uplift_factor?: number
  delay_days?: number
}

export interface SimulationEvent {
  event_id: string
  event_type: string
  timestamp: string
  payload: Record<string, unknown>
  metadata?: Record<string, unknown>
}

export interface SimulationMetrics {
  total_events: number
  event_counts: Record<string, number>
  total_orders: number
  avg_pick_time_minutes: number
  total_alerts: number
  start_time?: string
  end_time?: string
}

export interface SimulationResponse {
  scenario_type: string
  events: SimulationEvent[]
  metrics: SimulationMetrics
}
