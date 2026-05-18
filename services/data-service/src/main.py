"""FastAPI application for data-service."""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import get_processor, DataProcessor


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load data
    get_processor()
    yield
    # Shutdown: nothing special needed


app = FastAPI(
    title="DarkStore Data Service",
    description="Central data access service for DarkStore Analytics Platform",
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
    """Health check endpoint."""
    return {"status": "healthy", "service": "data-service"}


@app.get("/api/v1/data/kpis")
async def get_kpis():
    """Get summary KPIs for the dashboard."""
    processor = get_processor()
    return processor.get_summary_kpis()


@app.get("/api/v1/data/orders")
async def get_orders(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Get orders list with pagination."""
    processor = get_processor()
    orders = processor.get_orders(limit=limit, offset=offset)
    return {
        "orders": orders,
        "total": len(processor.orders_df),
        "limit": limit,
        "offset": offset
    }


@app.get("/api/v1/data/inventory")
async def get_inventory(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """Get inventory list with pagination."""
    processor = get_processor()
    items = processor.get_inventory(limit=limit, offset=offset)
    return {
        "items": items,
        "total": len(processor.inventory_df),
        "limit": limit,
        "offset": offset
    }


@app.get("/api/v1/data/inventory/low-stock")
async def get_low_stock(
    limit: int = Query(default=20, ge=1, le=100)
):
    """Get low stock items with recommendations."""
    processor = get_processor()
    items = processor.get_low_stock_items(limit=limit)
    return {
        "items": items,
        "total": len(items)
    }


@app.get("/api/v1/data/alerts")
async def get_alerts(
    limit: int = Query(default=50, ge=1, le=200)
):
    """Get active alerts sorted by severity."""
    processor = get_processor()
    alerts = processor.get_active_alerts(limit=limit)
    return {
        "alerts": alerts,
        "total": len(alerts)
    }


@app.get("/api/v1/data/staff/performance")
async def get_staff_performance():
    """Get staff performance metrics."""
    processor = get_processor()
    staff = processor.get_staff_performance()
    return {
        "staff": staff,
        "total": len(staff)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
