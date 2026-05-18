export interface OrderAnomaly {
  order_id: string
  timestamp: string
  num_items: number
  total_quantity: number
  fulfillment_time_minutes: number
  target_time_minutes: number
  assigned_staff: string
  status: string
  is_anomaly: boolean
  anomaly_score: number
  anomaly_type: string
  reason: string
}

export interface OrderAnomaliesResponse {
  anomalies: OrderAnomaly[]
  total: number
  contamination: number
}

export interface InventoryAnomaly {
  sku_id: string
  product_name: string
  category: string
  current_stock: number
  reorder_threshold: number
  expiry_date?: string
  anomaly_type: string
  reason: string
  stock_zscore: number
}

export interface InventoryAnomaliesResponse {
  anomalies: InventoryAnomaly[]
  total: number
}

export interface StaffAnomaly {
  staff_id: string
  anomaly_type: string
  reason: string
  total_orders: number
  avg_fulfillment_time: number
  delay_rate: number
}

export interface StaffAnomaliesResponse {
  anomalies: StaffAnomaly[]
  total: number
}
