export const COLORS = {
  cyan: '#06b6d4',
  emerald: '#10b981',
  violet: '#8b5cf6',
  rose: '#f43f5e',
  amber: '#f59e0b',
  blue: '#3b82f6',
}

export const STATUS_COLORS: Record<string, string> = {
  Pending: COLORS.amber,
  pending: COLORS.amber,
  Picking: COLORS.blue,
  picking: COLORS.blue,
  Packing: COLORS.violet,
  packing: COLORS.violet,
  Packed: COLORS.violet,
  packed: COLORS.violet,
  Delivered: COLORS.emerald,
  delivered: COLORS.emerald,
  Shipped: COLORS.cyan,
  shipped: COLORS.cyan,
  Cancelled: COLORS.rose,
  cancelled: COLORS.rose,
}

export const SEVERITY_COLORS: Record<string, string> = {
  critical: COLORS.rose,
  high: COLORS.amber,
  medium: '#eab308',
  low: COLORS.blue,
  info: COLORS.cyan,
}

export const CHART_MARGIN = { top: 10, right: 10, left: 0, bottom: 0 }
