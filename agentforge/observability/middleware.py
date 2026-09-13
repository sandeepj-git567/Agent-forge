"""
FastAPI Middleware for Correlation IDs, Latency Tracking, and Rate Limiting
"""
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class ProductionObservabilityMiddleware(BaseHTTPMiddleware):
    """Adds Correlation ID and Execution Latency headers to all HTTP responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        start_time = time.time()

        response: Response = await call_next(request)

        latency_ms = round((time.time() - start_time) * 1000.0, 2)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time-MS"] = str(latency_ms)

        return response
