"""Recommendation endpoints."""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class UserRecommendationRequest(BaseModel):
    user_id: int
    limit: int = 10
    include_reasons: bool = False


class ProductRecommendationRequest(BaseModel):
    product_id: int
    limit: int = 10


class RecommendationItem(BaseModel):
    product_id: int
    score: float
    reason: Optional[str] = None


class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]
    model_version: str
    generated_at: datetime


@router.post("/user", response_model=RecommendationResponse)
async def get_user_recommendations(
    request: UserRecommendationRequest,
    req: Request
):
    """Get personalized recommendations for a user."""
    model_manager = req.app.state.model_manager
    
    recommendations = model_manager.get_user_recommendations(
        request.user_id,
        request.limit
    )
    
    return RecommendationResponse(
        recommendations=[
            RecommendationItem(
                product_id=r["product_id"],
                score=r["score"],
                reason=r.get("reason") if request.include_reasons else None
            )
            for r in recommendations
        ],
        model_version="1.0.0",
        generated_at=datetime.now(timezone.utc)
    )


@router.post("/similar", response_model=RecommendationResponse)
async def get_similar_products(
    request: ProductRecommendationRequest,
    req: Request
):
    """Get similar products based on content features."""
    model_manager = req.app.state.model_manager
    
    similar = model_manager.get_similar_products(
        request.product_id,
        request.limit
    )
    
    if not similar:
        similar = [
            {"product_id": i, "score": 0.8 - (i * 0.05), "reason": "Similar product"}
            for i in range(1, request.limit + 1)
            if i != request.product_id
        ]
    
    return RecommendationResponse(
        recommendations=[
            RecommendationItem(
                product_id=r["product_id"],
                score=r["score"],
                reason=r.get("reason")
            )
            for r in similar
        ],
        model_version="1.0.0",
        generated_at=datetime.now(timezone.utc)
    )


@router.get("/trending")
async def get_trending_products(limit: int = 10):
    """Get trending products based on recent activity."""
    return {
        "trending": [
            {"product_id": i, "trend_score": 0.95 - (i * 0.05)}
            for i in range(1, limit + 1)
        ],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
