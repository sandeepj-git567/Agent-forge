"""
Tests for Observability, Telemetry, and Audit Logging
"""
import pytest
from fastapi.testclient import TestClient

from agentforge.api.main import app
from agentforge.db.models import AuditEvent
from agentforge.db.session import get_db_session
from agentforge.observability.metrics import TelemetryCollector
from agentforge.observability.tracer import MetricsRecorder

client = TestClient(app)


def test_telemetry_collector():
    collector = TelemetryCollector()
    collector.record_request(12.5, is_error=False)
    collector.record_request(45.0, is_error=True)
    collector.record_task_run()
    collector.record_rag_query()
    collector.record_evaluation()

    summary = collector.get_summary()
    assert summary["total_requests"] == 2
    assert summary["total_errors"] == 1
    assert summary["total_tasks_run"] == 1
    assert summary["total_rag_queries"] == 1
    assert summary["total_evaluations"] == 1
    assert summary["error_rate"] == 0.5
    assert summary["avg_latency_ms"] == 28.75


def test_observability_middleware_headers():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "X-Correlation-ID" in response.headers
    assert "X-Process-Time-MS" in response.headers
    # Custom correlation ID propagation
    response_custom = client.get("/api/v1/health", headers={"X-Correlation-ID": "test-correlation-123"})
    assert response_custom.headers["X-Correlation-ID"] == "test-correlation-123"


def test_log_audit_event():
    with get_db_session() as db_session:
        MetricsRecorder.log_audit_event(
            event_type="TEST_AUDIT",
            details={"action": "test_verification"},
            user_id="user-123",
            resource_type="document",
            resource_id="doc-456",
            db=db_session
        )

        evt = db_session.query(AuditEvent).filter_by(event_type="TEST_AUDIT").first()
        assert evt is not None
        assert evt.user_id == "user-123"
        assert evt.resource_type == "document"
        assert evt.resource_id == "doc-456"
        assert evt.details == {"action": "test_verification"}
