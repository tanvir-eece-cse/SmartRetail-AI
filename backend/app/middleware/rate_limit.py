"""Rate limiting middleware."""

import time
from collections import defaultdict
from typing import Callable, Dict, Tuple

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_requests = settings.RATE_LIMIT_REQUESTS
        self.rate_limit_period = settings.RATE_LIMIT_PERIOD
        self.request_counts: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit and process request."""
        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/v1/health", "/metrics"]:
            return await call_next(request)
        
        # Check rate limit
        current_time = time.time()
        count, window_start = self.request_counts[client_ip]
        
        # Reset window if expired
        if current_time - window_start >= self.rate_limit_period:
            self.request_counts[client_ip] = (1, current_time)
        elif count >= self.rate_limit_requests:
            # Rate limit exceeded
            retry_after = int(self.rate_limit_period - (current_time - window_start))
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        else:
            self.request_counts[client_ip] = (count + 1, window_start)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.rate_limit_requests - self.request_counts[client_ip][0]
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(
            int(self.request_counts[client_ip][1] + self.rate_limit_period)
        )
        
        return response
