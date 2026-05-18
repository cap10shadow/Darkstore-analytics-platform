"""FastAPI application for affinity-analyzer-service."""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .analyzer import get_analyzer


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_analyzer()
    yield


app = FastAPI(
    title="DarkStore Affinity Analyzer Service",
    description="Product affinity analysis service for co-purchase patterns",
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
    return {"status": "healthy", "service": "affinity-analyzer-service"}


@app.get("/api/v1/affinity/pairs")
async def get_affinity_pairs(
    top_n: int = Query(default=20, ge=1, le=100, description="Number of top pairs"),
    min_lift: float = Query(default=1.0, ge=0.5, le=5.0, description="Minimum lift threshold")
):
    """Get top co-purchased item pairs."""
    analyzer = get_analyzer()
    pairs = analyzer.get_top_pairs(top_n=top_n, min_lift=min_lift)

    return {
        "pairs": pairs,
        "total": len(pairs)
    }


@app.get("/api/v1/affinity/recommendations")
async def get_colocation_recommendations(
    distance_threshold: int = Query(default=50, ge=10, le=200, description="Maximum acceptable distance")
):
    """Get placement recommendations for co-locating frequently purchased items."""
    analyzer = get_analyzer()
    recommendations = analyzer.get_colocation_recommendations(distance_threshold=distance_threshold)

    return {
        "recommendations": recommendations,
        "total": len(recommendations)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
