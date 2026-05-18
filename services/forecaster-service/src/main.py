"""FastAPI application for forecaster-service."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from contextlib import asynccontextmanager

from .forecaster import get_forecaster


class ForecastRequest(BaseModel):
    sku_id: str = Field(..., description="SKU identifier")
    forecast_days: int = Field(default=14, ge=1, le=90, description="Number of days to forecast")
    mode: str = Field(default="auto", description="Forecasting mode: auto, ensemble, or model name")


class CompareRequest(BaseModel):
    sku_id: str = Field(..., description="SKU identifier")
    forecast_days: int = Field(default=14, ge=1, le=90, description="Number of days to forecast")


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_forecaster()
    yield


app = FastAPI(
    title="DarkStore Forecaster Service",
    description="Demand forecasting service with multi-model support",
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
    return {"status": "healthy", "service": "forecaster-service"}


@app.post("/api/v1/forecast/sku")
async def forecast_sku(request: ForecastRequest):
    """Forecast demand for a single SKU."""
    forecaster = get_forecaster()
    result = forecaster.forecast_sku(
        sku_id=request.sku_id,
        forecast_days=request.forecast_days,
        mode=request.mode
    )

    if not result.get('has_data', False) and 'error' not in result:
        raise HTTPException(status_code=404, detail=result.get('message', 'SKU not found'))

    return result


@app.post("/api/v1/forecast/compare")
async def compare_models(request: CompareRequest):
    """Compare all models for a specific SKU."""
    forecaster = get_forecaster()
    result = forecaster.compare_models(
        sku_id=request.sku_id,
        forecast_days=request.forecast_days
    )

    if 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
