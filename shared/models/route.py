"""Route optimization models for route-optimizer-service."""
from pydantic import BaseModel, Field
from typing import List, Tuple
from enum import Enum


class OptimizationMethod(str, Enum):
    NN = "nn"  # Nearest neighbor
    TWO_OPT = "2opt"  # 2-opt improvement
    NN_TWO_OPT = "nn+2opt"  # Combined (default)


class RouteOptimizeRequest(BaseModel):
    pick_list: List[str] = Field(..., description="List of shelf locations to visit (e.g., ['A05-3', 'B12-2'])")
    method: OptimizationMethod = Field(default=OptimizationMethod.NN_TWO_OPT, description="Optimization method")


class RouteOptimizeResponse(BaseModel):
    route: List[str] = Field(..., description="Optimized route including ENTRANCE and PACKING")
    coordinates: List[Tuple[float, float]] = Field(..., description="Coordinates for each stop")
    distance: float = Field(..., description="Total optimized distance")
    naive_distance: float = Field(..., description="Distance without optimization")
    estimated_time_minutes: float = Field(..., description="Estimated completion time")
    improvement_percent: float = Field(..., description="Improvement over naive route")
    num_stops: int = Field(..., description="Number of picking stops")


class BatchRouteRequest(BaseModel):
    orders_pick_lists: List[List[str]] = Field(..., description="List of pick lists, one per order")
    picker_capacity: int = Field(default=8, ge=1, le=20, description="Maximum items a picker can carry")


class BatchRouteResponse(BaseModel):
    batches: List[RouteOptimizeResponse]
    total_batches: int
    total_items: int
    total_distance: float
    total_time_minutes: float
