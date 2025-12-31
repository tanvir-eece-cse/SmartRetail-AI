"""
SmartRetail-AI ML Service
Machine Learning service for product recommendations, customer segmentation, and analytics.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
import structlog

from app.api.v1.router import api_router
from app.core.config import settings
from app.services.model_manager import ModelManager

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan handler."""
    logger.info("Starting SmartRetail-AI ML Service", version=settings.APP_VERSION)
    
    # Initialize model manager and load models
    model_manager = ModelManager()
    await model_manager.load_models()
    app.state.model_manager = model_manager
    
    logger.info("ML models loaded successfully")
    
    yield
    
    logger.info("Shutting down ML Service")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="SmartRetail-AI ML Service",
        description="""
## SmartRetail-AI ML Service API

Machine Learning service providing:
- **Product Recommendations** - Collaborative filtering and content-based recommendations
- **Customer Segmentation** - RFM analysis and clustering
- **Demand Forecasting** - Time series predictions
- **Sentiment Analysis** - Product review analysis
- **Churn Prediction** - At-risk customer identification

### Author
**Md. Tanvir Hossain**
- GitHub: [tanvir-eece-cse](https://github.com/tanvir-eece-cse)
        """,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(api_router, prefix="/api/v1")
    
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    return app


app = create_application()


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": "SmartRetail-AI ML Service",
        "version": settings.APP_VERSION,
        "description": "ML-powered recommendations and analytics",
        "endpoints": {
            "recommendations": "/api/v1/recommendations",
            "segmentation": "/api/v1/segmentation",
            "forecasting": "/api/v1/forecasting",
            "sentiment": "/api/v1/sentiment"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "models_loaded": True
    }
