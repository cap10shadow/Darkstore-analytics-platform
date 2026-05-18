"""FastAPI application for event-simulator-service."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from contextlib import asynccontextmanager

from .simulator import get_simulator


class SimulationRequest(BaseModel):
    scenario_type: str = Field(..., description="Type of scenario: normal, flash_sale, or supply_delay")
    duration_hours: int = Field(default=8, ge=1, le=24, description="Duration of simulation in hours")
    orders_per_hour: Optional[int] = Field(default=20, description="For normal scenario")
    uplift_factor: Optional[float] = Field(default=5.0, description="For flash_sale scenario")
    delay_days: Optional[int] = Field(default=3, description="For supply_delay scenario")


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_simulator()
    yield


app = FastAPI(
    title="DarkStore Event Simulator Service",
    description="Event simulation service for scenario testing",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "event-simulator-service"}


@app.post("/api/v1/simulate/scenario")
async def run_simulation(request: SimulationRequest):
    """Run a simulation scenario."""
    simulator = get_simulator()

    if request.scenario_type not in ['normal', 'flash_sale', 'supply_delay']:
        raise HTTPException(status_code=400, detail="Invalid scenario type")

    kwargs = {}
    if request.scenario_type == 'normal':
        kwargs['duration_hours'] = request.duration_hours
        kwargs['orders_per_hour'] = request.orders_per_hour
    elif request.scenario_type == 'flash_sale':
        kwargs['duration_hours'] = request.duration_hours
        kwargs['uplift_factor'] = request.uplift_factor
    elif request.scenario_type == 'supply_delay':
        kwargs['delay_days'] = request.delay_days

    start_time = datetime.now()
    events = simulator.generate_scenario(request.scenario_type, start_time, **kwargs)
    metrics = simulator.get_metrics()

    events_dicts = [e.to_dict() for e in events]

    return {
        "scenario_type": request.scenario_type,
        "events": events_dicts,
        "metrics": metrics
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
