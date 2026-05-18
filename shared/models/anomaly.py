"""Anomaly detection models for anomaly-detector-service."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class OrderAnomaly(BaseModel):
    order_id: str
    timestamp: datetime
    num_items: int
    total_quantity: int
    fulfillment_time_minutes: float
    target_time_minutes: int
    assigned_staff: str
    status: str
    is_anomaly: bool
    anomaly_score: float
    anomaly_type: str
    reason: str


class InventoryAnomaly(BaseModel):
    sku_id: str
    product_name: str
    category: str
    current_stock: int
    reorder_threshold: int
    expiry_date: Optional[datetime] = None
    anomaly_type: str
    reason: str
    stock_zscore: float


class StaffAnomaly(BaseModel):
    staff_id: str
    anomaly_type: str
    reason: str
    total_orders: int
    avg_fulfillment_time: float
    delay_rate: float


class OrderAnomalyRequest(BaseModel):
    contamination: float = Field(default=0.05, ge=0.01, le=0.2, description="Expected proportion of anomalies")


class OrderAnomaliesResponse(BaseModel):
    anomalies: List[OrderAnomaly]
    total: int
    contamination: float


class InventoryAnomaliesResponse(BaseModel):
    anomalies: List[InventoryAnomaly]
    total: int


class StaffAnomaliesResponse(BaseModel):
    anomalies: List[StaffAnomaly]
    total: int
