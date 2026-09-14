"""
FastAPI Middleware for Correlation IDs, Latency Tracking, Telemetry, and Observability
"""
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from agentforge.observability.metrics import default_telemetry_collector


class ProductionObservabilityMiddleware(BaseHTTPMiddleware):
    """Adds Correlation ID and Execution Latency headers to HTTP responses and updates telemetry metrics."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        start_time = time.time()

        try:
            response: Response = await call_next(request)
            latency_ms = round((time.time() - start_time) * 1000.0, 2)

            is_error = response.status_code >= 400
            default_telemetry_collector.record_request(latency_ms, is_error=is_error)

            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Process-Time-MS"] = str(latency_ms)

            return response
        except Exception:
            latency_ms = round((time.time() - start_time) * 1000.0, 2)
            default_telemetry_collector.record_request(latency_ms, is_error=True)
            raise
