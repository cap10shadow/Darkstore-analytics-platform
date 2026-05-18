"""FastAPI application for route-optimizer-service."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List

from .optimizer import get_optimizer


class RouteOptimizeRequest(BaseModel):
    pick_list: List[str] = Field(..., description="List of shelf locations to visit")
    method: str = Field(default="nn+2opt", description="Optimization method: nn, 2opt, or nn+2opt")


class BatchRouteRequest(BaseModel):
    orders_pick_lists: List[List[str]] = Field(..., description="List of pick lists, one per order")
    picker_capacity: int = Field(default=8, ge=1, le=20, description="Maximum items a picker can carry")


app = FastAPI(
    title="DarkStore Route Optimizer Service",
    description="Route optimization service for warehouse picking operations",
    version="1.0.0"
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
    return {"status": "healthy", "service": "route-optimizer-service"}


@app.post("/api/v1/routes/optimize")
async def optimize_route(request: RouteOptimizeRequest):
    """Optimize picking route for a single order."""
    optimizer = get_optimizer()

    if request.method not in ['nn', '2opt', 'nn+2opt']:
        raise HTTPException(status_code=400, detail="Invalid method. Use 'nn', '2opt', or 'nn+2opt'")

    result = optimizer.optimize_route(request.pick_list, method=request.method)
    return result


@app.post("/api/v1/routes/batch")
async def batch_optimize(request: BatchRouteRequest):
    """Optimize routes for batched orders."""
    optimizer = get_optimizer()

    batches = optimizer.batch_route(
        orders_pick_lists=request.orders_pick_lists,
        picker_capacity=request.picker_capacity
    )

    total_items = sum(len(pl) for pl in request.orders_pick_lists)
    total_distance = sum(b['distance'] for b in batches)
    total_time = sum(b['estimated_time_minutes'] for b in batches)

    return {
        "batches": batches,
        "total_batches": len(batches),
        "total_items": total_items,
        "total_distance": round(total_distance, 2),
        "total_time_minutes": round(total_time, 2)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
