"""Affinity analysis models for affinity-analyzer-service."""
from pydantic import BaseModel, Field
from typing import List, Optional


class AffinityPair(BaseModel):
    sku_a: str
    product_a: str
    category_a: str
    location_a: str
    sku_b: str
    product_b: str
    category_b: str
    location_b: str
    co_occurrences: int
    confidence_a_to_b: float
    lift: float
    affinity_score: float


class ColocationRecommendation(BaseModel):
    sku_a: str
    sku_b: str
    product_a: str
    product_b: str
    current_distance: float
    co_occurrences_weekly: int
    affinity_score: float
    lift: float
    estimated_annual_time_saved_hours: float
    recommendation: str
    priority: str


class AffinityPairsRequest(BaseModel):
    top_n: int = Field(default=20, ge=1, le=100, description="Number of top pairs to return")
    min_lift: float = Field(default=1.0, ge=0.5, le=5.0, description="Minimum lift threshold")


class AffinityPairsResponse(BaseModel):
    pairs: List[AffinityPair]
    total: int


class ColocationRequest(BaseModel):
    distance_threshold: int = Field(default=50, ge=10, le=200, description="Maximum acceptable distance between items")


class ColocationResponse(BaseModel):
    recommendations: List[ColocationRecommendation]
    total: int
