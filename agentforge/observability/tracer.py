"""
OpenTelemetry Tracing, Audit Event Logger, and Observability Metrics for AgentForge AI
"""
import logging
import time
from typing import Any

from opentelemetry import trace
from sqlalchemy.orm import Session

from agentforge.db.models import AuditEvent

logger = logging.getLogger("agentforge.observability")
tracer = trace.get_tracer("agentforge.tracer", "1.0.0")


class MetricsRecorder:
    """Records token usage, latency metrics, OpenTelemetry spans, and audit events safely."""

    @staticmethod
    def record_span(name: str, attributes: dict[str, Any] | None = None):
        """Create an OpenTelemetry trace span."""
        return tracer.start_as_current_span(name, attributes=attributes or {})

    @staticmethod
    def calculate_latency_ms(start_time: float) -> float:
        """Calculate elapsed latency in milliseconds."""
        return round((time.time() - start_time) * 1000.0, 2)

    @staticmethod
    def log_audit_event(
        event_type: str,
        details: dict[str, Any],
        user_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        db: Session | None = None
    ) -> None:
        """
        Record a structured security/execution audit event.
        Persists in AuditEvent database table if db session is provided.
        """
        logger.info(f"AUDIT_EVENT [{event_type}]: user={user_id} resource={resource_type}:{resource_id} details={details}")

        if db:
            try:
                evt = AuditEvent(
                    user_id=user_id,
                    event_type=event_type,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details
                )
                db.add(evt)
                db.commit()
            except Exception as err:
                logger.warning(f"Failed to persist AuditEvent: {err}")


default_metrics_recorder = MetricsRecorder()
