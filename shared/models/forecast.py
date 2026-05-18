"""Forecast models for forecaster-service."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ForecastMode(str, Enum):
    AUTO = "auto"
    ENSEMBLE = "ensemble"
    ARIMA = "arima"
    SARIMA = "sarima"
    HOLT_WINTERS = "holt_winters"
    RF = "rf"
    GBM = "gbm"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    PROPHET = "prophet"


class ForecastRequest(BaseModel):
    sku_id: str = Field(..., description="SKU identifier")
    forecast_days: int = Field(default=14, ge=1, le=90, description="Number of days to forecast")
    mode: ForecastMode = Field(default=ForecastMode.AUTO, description="Forecasting mode")


class ForecastResponse(BaseModel):
    sku_id: str
    has_data: bool
    message: Optional[str] = None
    model_used: Optional[str] = None
    historical_days: Optional[int] = None
    historical_demand: Optional[List[float]] = None
    historical_dates: Optional[List[str]] = None
    forecast_days: Optional[int] = None
    forecast: Optional[List[float]] = None
    lower_ci: Optional[List[float]] = None
    upper_ci: Optional[List[float]] = None
    forecast_dates: Optional[List[str]] = None
    avg_historical_daily: Optional[float] = None
    avg_forecast_daily: Optional[float] = None
    trend: Optional[str] = None
    total_forecast_demand: Optional[float] = None
    all_models: Optional[List[str]] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    current_stock: Optional[int] = None
    reorder_threshold: Optional[int] = None
    needs_reorder: Optional[bool] = None


class ModelComparison(BaseModel):
    sku_id: str
    models: Dict[str, Any]
    data_length: int
    data_warning: Optional[str] = None
    error: Optional[str] = None


class CompareRequest(BaseModel):
    sku_id: str = Field(..., description="SKU identifier")
    forecast_days: int = Field(default=14, ge=1, le=90, description="Number of days to forecast")
