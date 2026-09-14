"""
FastAPI Pure ASGI Middleware for Correlation IDs, Latency Tracking, Telemetry, and Observability
"""
import time
import uuid

from agentforge.observability.metrics import default_telemetry_collector


class ProductionObservabilityMiddleware:
    """Adds Correlation ID and Execution Latency headers to HTTP responses and updates telemetry metrics."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers_dict = dict(scope.get("headers", []))
        correlation_id_bytes = headers_dict.get(b"x-correlation-id")
        correlation_id = correlation_id_bytes.decode("utf-8") if correlation_id_bytes else str(uuid.uuid4())
        start_time = time.time()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
                latency_ms = round((time.time() - start_time) * 1000.0, 2)
                is_error = status_code >= 400
                default_telemetry_collector.record_request(latency_ms, is_error=is_error)

                headers_list = list(message.get("headers", []))
                headers_list.append((b"x-correlation-id", correlation_id.encode("utf-8")))
                headers_list.append((b"x-process-time-ms", str(latency_ms).encode("utf-8")))
                message["headers"] = headers_list

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            latency_ms = round((time.time() - start_time) * 1000.0, 2)
            default_telemetry_collector.record_request(latency_ms, is_error=True)
            raise
