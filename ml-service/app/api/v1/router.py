"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import recommendations, segmentation, forecasting, sentiment

api_router = APIRouter()

api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["Recommendations"]
)
api_router.include_router(
    segmentation.router,
    prefix="/segmentation",
    tags=["Customer Segmentation"]
)
api_router.include_router(
    forecasting.router,
    prefix="/forecasting",
    tags=["Demand Forecasting"]
)
api_router.include_router(
    sentiment.router,
    prefix="/sentiment",
    tags=["Sentiment Analysis"]
)
