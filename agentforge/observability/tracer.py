"""
OpenTelemetry Tracing and Observability Metrics for AgentForge AI
"""
import time
from typing import Any

from opentelemetry import trace

tracer = trace.get_tracer("agentforge.tracer", "1.0.0")


class MetricsRecorder:
    """Records token usage, latency metrics, and execution spans safely."""

    @staticmethod
    def record_span(name: str, attributes: dict[str, Any] | None = None):
        """Create an OpenTelemetry trace span."""
        return tracer.start_as_current_span(name, attributes=attributes or {})

    @staticmethod
    def calculate_latency_ms(start_time: float) -> float:
        """Calculate elapsed latency in milliseconds."""
        return round((time.time() - start_time) * 1000.0, 2)


default_metrics_recorder = MetricsRecorder()
