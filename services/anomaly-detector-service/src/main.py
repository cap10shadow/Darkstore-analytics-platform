"""FastAPI application for anomaly-detector-service."""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

from .detector import get_detector


class OrderAnomalyRequest(BaseModel):
    contamination: float = Field(default=0.05, ge=0.01, le=0.2, description="Expected proportion of anomalies")


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_detector()
    yield


app = FastAPI(
    title="DarkStore Anomaly Detector Service",
    description="Anomaly detection service for operational monitoring",
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
    return {"status": "healthy", "service": "anomaly-detector-service"}


@app.post("/api/v1/anomalies/orders")
async def detect_order_anomalies(request: OrderAnomalyRequest):
    """Detect anomalous order fulfillment using Isolation Forest."""
    detector = get_detector()
    anomalies = detector.detect_order_fulfillment_anomalies(contamination=request.contamination)

    return {
        "anomalies": anomalies,
        "total": len(anomalies),
        "contamination": request.contamination
    }


@app.get("/api/v1/anomalies/inventory")
async def detect_inventory_anomalies():
    """Detect inventory anomalies using Z-score method."""
    detector = get_detector()
    anomalies = detector.detect_inventory_anomalies()

    return {
        "anomalies": anomalies,
        "total": len(anomalies)
    }


@app.get("/api/v1/anomalies/staff")
async def detect_staff_anomalies():
    """Detect staff performance anomalies."""
    detector = get_detector()
    anomalies = detector.detect_staff_performance_anomalies()

    return {
        "anomalies": anomalies,
        "total": len(anomalies)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
