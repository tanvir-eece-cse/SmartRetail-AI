"""
SmartRetail-AI Backend API
A comprehensive e-commerce analytics and recommendation platform.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import structlog

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

# Configure structured logging
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
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("Starting SmartRetail-AI Backend", version=settings.APP_VERSION)
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SmartRetail-AI Backend")
    await engine.dispose()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="SmartRetail-AI API",
        description="""
## SmartRetail-AI Backend API

A production-ready e-commerce analytics and recommendation platform API.

### Features
- **User Authentication** - JWT-based authentication with OAuth2
- **Product Management** - Full CRUD operations for products
- **Recommendations** - AI-powered product recommendations
- **Analytics** - Sales, customer, and product analytics
- **Search** - Full-text search capabilities

### Author
**Md. Tanvir Hossain**
- GitHub: [tanvir-eece-cse](https://github.com/tanvir-eece-cse)
- LinkedIn: [tanvir-eece](https://linkedin.com/in/tanvir-eece)
        """,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    
    # Include API routers
    app.include_router(api_router, prefix="/api/v1")
    
    # Mount Prometheus metrics
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    return app


app = create_application()


@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint returning API information."""
    return {
        "name": "SmartRetail-AI API",
        "version": settings.APP_VERSION,
        "description": "AI-Powered E-commerce Analytics & Recommendation Platform",
        "docs": "/docs",
        "health": "/health",
        "author": {
            "name": "Md. Tanvir Hossain",
            "github": "https://github.com/tanvir-eece-cse",
            "linkedin": "https://linkedin.com/in/tanvir-eece",
            "email": "tanvir.eece.mist@gmail.com"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled errors."""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "error_id": str(id(exc))
        }
    )
