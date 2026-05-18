"""Simulation models for event-simulator-service."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ScenarioType(str, Enum):
    NORMAL = "normal"
    FLASH_SALE = "flash_sale"
    SUPPLY_DELAY = "supply_delay"


class SimulationRequest(BaseModel):
    scenario_type: ScenarioType = Field(..., description="Type of scenario to simulate")
    duration_hours: int = Field(default=8, ge=1, le=24, description="Duration of simulation in hours")
    # Scenario-specific parameters
    orders_per_hour: Optional[int] = Field(default=20, description="For normal scenario")
    uplift_factor: Optional[float] = Field(default=5.0, description="For flash_sale scenario")
    delay_days: Optional[int] = Field(default=3, description="For supply_delay scenario")


class SimulationEvent(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    payload: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class SimulationMetrics(BaseModel):
    total_events: int
    event_counts: Dict[str, int]
    total_orders: int
    avg_pick_time_minutes: float
    total_alerts: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class SimulationResponse(BaseModel):
    scenario_type: str
    events: List[SimulationEvent]
    metrics: SimulationMetrics
