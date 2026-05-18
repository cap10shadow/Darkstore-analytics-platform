export interface KPIs {
  total_orders_today: number
  total_orders_all: number
  on_time_rate: number
  backlog: number
  avg_fulfillment_minutes: number
  total_revenue: number
  revenue_today: number
  low_stock_count: number
  total_skus: number
  stock_health_rate: number
  active_alerts: number
  critical_alerts: number
}

export interface OrderItem {
  sku: string
  qty: number
}

export interface Order {
  order_id: string
  timestamp: string
  num_items: number
  total_quantity: number
  total_value: number
  status: string
  assigned_staff: string
  fulfillment_time_minutes: number
  is_delayed: boolean
  target_time_minutes: number
  items: OrderItem[]
}

export interface OrdersResponse {
  orders: Order[]
  total: number
  limit: number
  offset: number
}

export interface InventoryItem {
  sku_id: string
  product_name: string
  category: string
  current_stock: number
  reorder_threshold: number
  shelf_location: string
  unit_price: number
  expiry_date?: string
  demand_rate: string
  health_status?: string
  days_until_expiry?: number
}

export interface InventoryResponse {
  items: InventoryItem[]
  total: number
  limit: number
  offset: number
}

export interface LowStockItem {
  sku_id: string
  product_name: string
  category: string
  current_stock: number
  reorder_threshold: number
  stock_percentage: number
  daily_demand?: number
  days_until_stockout?: number
  recommended_order_qty?: number
  estimated_cost?: number
}

export interface LowStockResponse {
  items: LowStockItem[]
  total: number
}

export interface Alert {
  alert_id: string
  alert_type: string
  severity: string
  status: string
  timestamp: string
  related_sku?: string
  related_order?: string
  message: string
  recommendation?: string
}

export interface AlertsResponse {
  alerts: Alert[]
  total: number
}

export interface StaffPerformance {
  staff_id: string
  name: string
  role: string
  orders_completed: number
  avg_fulfillment_time: number
  delays_caused: number
  orders_per_hour: number
  delay_rate: number
}

export interface StaffPerformanceResponse {
  staff: StaffPerformance[]
  total: number
}
