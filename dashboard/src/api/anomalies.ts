import { get, post } from './client'
import type { OrderAnomaliesResponse, InventoryAnomaliesResponse, StaffAnomaliesResponse } from '../types/anomalies'

export const detectOrderAnomalies = (contamination = 0.05) =>
  post<OrderAnomaliesResponse>('/api/v1/anomalies/orders', { contamination })

export const detectInventoryAnomalies = () =>
  get<InventoryAnomaliesResponse>('/api/v1/anomalies/inventory')

export const detectStaffAnomalies = () =>
  get<StaffAnomaliesResponse>('/api/v1/anomalies/staff')
