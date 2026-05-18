"""Data models for data-service."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class KPIsResponse(BaseModel):
    total_orders_today: int
    total_orders_all: int
    on_time_rate: float
    backlog: int
    avg_fulfillment_minutes: float
    total_revenue: float
    revenue_today: float
    low_stock_count: int
    total_skus: int
    stock_health_rate: float
    active_alerts: int
    critical_alerts: int


class OrderItem(BaseModel):
    sku: str
    qty: int


class Order(BaseModel):
    order_id: str
    timestamp: datetime
    num_items: int
    total_quantity: int
    total_value: float
    status: str
    assigned_staff: str
    fulfillment_time_minutes: float
    is_delayed: bool
    target_time_minutes: int
    items: List[OrderItem]


class InventoryItem(BaseModel):
    sku_id: str
    product_name: str
    category: str
    current_stock: int
    reorder_threshold: int
    shelf_location: str
    unit_price: float
    expiry_date: Optional[datetime] = None
    demand_rate: str
    health_status: Optional[str] = None
    days_until_expiry: Optional[float] = None


class LowStockItem(BaseModel):
    sku_id: str
    product_name: str
    category: str
    current_stock: int
    reorder_threshold: int
    stock_percentage: float
    daily_demand: Optional[float] = None
    days_until_stockout: Optional[float] = None
    recommended_order_qty: Optional[int] = None
    estimated_cost: Optional[float] = None


class Alert(BaseModel):
    alert_id: str
    alert_type: str
    severity: str
    status: str
    timestamp: datetime
    related_sku: Optional[str] = None
    related_order: Optional[str] = None
    message: str
    recommendation: Optional[str] = None


class StaffPerformance(BaseModel):
    staff_id: str
    name: str
    role: str
    orders_completed: int
    avg_fulfillment_time: float
    delays_caused: int
    orders_per_hour: float
    delay_rate: float


class OrdersResponse(BaseModel):
    orders: List[Order]
    total: int


class InventoryResponse(BaseModel):
    items: List[InventoryItem]
    total: int


class LowStockResponse(BaseModel):
    items: List[LowStockItem]
    total: int


class AlertsResponse(BaseModel):
    alerts: List[Alert]
    total: int


class StaffPerformanceResponse(BaseModel):
    staff: List[StaffPerformance]
    total: int
