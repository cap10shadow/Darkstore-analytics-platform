"""FastAPI API Gateway for DarkStore Analytics Platform."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from typing import Dict, Any
import os

# Service URLs (configurable via environment variables)
DATA_SERVICE_URL = os.getenv("DATA_SERVICE_URL", "http://localhost:8001")
FORECASTER_SERVICE_URL = os.getenv("FORECASTER_SERVICE_URL", "http://localhost:8002")
ROUTE_OPTIMIZER_SERVICE_URL = os.getenv("ROUTE_OPTIMIZER_SERVICE_URL", "http://localhost:8003")
ANOMALY_DETECTOR_SERVICE_URL = os.getenv("ANOMALY_DETECTOR_SERVICE_URL", "http://localhost:8004")
AFFINITY_ANALYZER_SERVICE_URL = os.getenv("AFFINITY_ANALYZER_SERVICE_URL", "http://localhost:8005")
EVENT_SIMULATOR_SERVICE_URL = os.getenv("EVENT_SIMULATOR_SERVICE_URL", "http://localhost:8006")

SERVICE_MAP = {
    "data": DATA_SERVICE_URL,
    "forecast": FORECASTER_SERVICE_URL,
    "routes": ROUTE_OPTIMIZER_SERVICE_URL,
    "anomalies": ANOMALY_DETECTOR_SERVICE_URL,
    "affinity": AFFINITY_ANALYZER_SERVICE_URL,
    "simulate": EVENT_SIMULATOR_SERVICE_URL,
}

app = FastAPI(
    title="DarkStore API Gateway",
    description="API Gateway for DarkStore Analytics Platform microservices",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def proxy_request(service_url: str, path: str, method: str = "GET",
                       params: Dict = None, json_data: Any = None) -> Dict:
    """Proxy request to a downstream service."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        url = f"{service_url}{path}"
        try:
            if method == "GET":
                response = await client.get(url, params=params)
            elif method == "POST":
                response = await client.post(url, json=json_data, params=params)
            else:
                raise HTTPException(status_code=405, detail=f"Method {method} not allowed")

            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            return response.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {service_url}")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Request timed out")


@app.get("/health")
async def health_check():
    """Gateway health check."""
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/health/all")
async def all_services_health():
    """Check health of all services."""
    health_status = {"api-gateway": "healthy"}

    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, service_url in SERVICE_MAP.items():
            try:
                response = await client.get(f"{service_url}/health")
                if response.status_code == 200:
                    health_status[service_name] = "healthy"
                else:
                    health_status[service_name] = "unhealthy"
            except Exception:
                health_status[service_name] = "unavailable"

    return health_status


# ==================== DATA SERVICE ROUTES ====================

@app.get("/api/v1/data/kpis")
async def get_kpis():
    """Get summary KPIs."""
    return await proxy_request(DATA_SERVICE_URL, "/api/v1/data/kpis")


@app.get("/api/v1/data/orders")
async def get_orders(limit: int = 100, offset: int = 0):
    """Get orders list."""
    return await proxy_request(DATA_SERVICE_URL, "/api/v1/data/orders",
                               params={"limit": limit, "offset": offset})


@app.get("/api/v1/data/inventory")
async def get_inventory(limit: int = 100, offset: int = 0):
    """Get inventory list."""
    return await proxy_request(DATA_SERVICE_URL, "/api/v1/data/inventory",
                               params={"limit": limit, "offset": offset})


@app.get("/api/v1/data/inventory/low-stock")
async def get_low_stock(limit: int = 20):
    """Get low stock items."""
    return await proxy_request(DATA_SERVICE_URL, "/api/v1/data/inventory/low-stock",
                               params={"limit": limit})


@app.get("/api/v1/data/alerts")
async def get_alerts(limit: int = 50):
    """Get active alerts."""
    return await proxy_request(DATA_SERVICE_URL, "/api/v1/data/alerts",
                               params={"limit": limit})


@app.get("/api/v1/data/staff/performance")
async def get_staff_performance():
    """Get staff performance metrics."""
    return await proxy_request(DATA_SERVICE_URL, "/api/v1/data/staff/performance")


# ==================== FORECASTER SERVICE ROUTES ====================

@app.post("/api/v1/forecast/sku")
async def forecast_sku(request: Request):
    """Forecast demand for a SKU."""
    json_data = await request.json()
    return await proxy_request(FORECASTER_SERVICE_URL, "/api/v1/forecast/sku",
                               method="POST", json_data=json_data)


@app.post("/api/v1/forecast/compare")
async def compare_models(request: Request):
    """Compare forecast models for a SKU."""
    json_data = await request.json()
    return await proxy_request(FORECASTER_SERVICE_URL, "/api/v1/forecast/compare",
                               method="POST", json_data=json_data)


# ==================== ROUTE OPTIMIZER SERVICE ROUTES ====================

@app.post("/api/v1/routes/optimize")
async def optimize_route(request: Request):
    """Optimize picking route."""
    json_data = await request.json()
    return await proxy_request(ROUTE_OPTIMIZER_SERVICE_URL, "/api/v1/routes/optimize",
                               method="POST", json_data=json_data)


@app.post("/api/v1/routes/batch")
async def batch_optimize(request: Request):
    """Batch optimize routes."""
    json_data = await request.json()
    return await proxy_request(ROUTE_OPTIMIZER_SERVICE_URL, "/api/v1/routes/batch",
                               method="POST", json_data=json_data)


# ==================== ANOMALY DETECTOR SERVICE ROUTES ====================

@app.post("/api/v1/anomalies/orders")
async def detect_order_anomalies(request: Request):
    """Detect order anomalies."""
    json_data = await request.json()
    return await proxy_request(ANOMALY_DETECTOR_SERVICE_URL, "/api/v1/anomalies/orders",
                               method="POST", json_data=json_data)


@app.get("/api/v1/anomalies/inventory")
async def detect_inventory_anomalies():
    """Detect inventory anomalies."""
    return await proxy_request(ANOMALY_DETECTOR_SERVICE_URL, "/api/v1/anomalies/inventory")


@app.get("/api/v1/anomalies/staff")
async def detect_staff_anomalies():
    """Detect staff performance anomalies."""
    return await proxy_request(ANOMALY_DETECTOR_SERVICE_URL, "/api/v1/anomalies/staff")


# ==================== AFFINITY ANALYZER SERVICE ROUTES ====================

@app.get("/api/v1/affinity/pairs")
async def get_affinity_pairs(top_n: int = 20, min_lift: float = 1.0):
    """Get product affinity pairs."""
    return await proxy_request(AFFINITY_ANALYZER_SERVICE_URL, "/api/v1/affinity/pairs",
                               params={"top_n": top_n, "min_lift": min_lift})


@app.get("/api/v1/affinity/recommendations")
async def get_colocation_recommendations(distance_threshold: int = 50):
    """Get co-location recommendations."""
    return await proxy_request(AFFINITY_ANALYZER_SERVICE_URL, "/api/v1/affinity/recommendations",
                               params={"distance_threshold": distance_threshold})


# ==================== EVENT SIMULATOR SERVICE ROUTES ====================

@app.post("/api/v1/simulate/scenario")
async def run_simulation(request: Request):
    """Run a simulation scenario."""
    json_data = await request.json()
    return await proxy_request(EVENT_SIMULATOR_SERVICE_URL, "/api/v1/simulate/scenario",
                               method="POST", json_data=json_data)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
