import { get } from './client'
import type { KPIs, OrdersResponse, InventoryResponse, LowStockResponse, AlertsResponse, StaffPerformanceResponse } from '../types/data'

export const fetchKPIs = () => get<KPIs>('/api/v1/data/kpis')

export const fetchOrders = (limit = 1000, offset = 0) =>
  get<OrdersResponse>(`/api/v1/data/orders?limit=${limit}&offset=${offset}`)

export const fetchInventory = (limit = 1000, offset = 0) =>
  get<InventoryResponse>(`/api/v1/data/inventory?limit=${limit}&offset=${offset}`)

export const fetchLowStock = (limit = 100) =>
  get<LowStockResponse>(`/api/v1/data/inventory/low-stock?limit=${limit}`)

export const fetchAlerts = (limit = 200) =>
  get<AlertsResponse>(`/api/v1/data/alerts?limit=${limit}`)

export const fetchStaffPerformance = () =>
  get<StaffPerformanceResponse>('/api/v1/data/staff/performance')
