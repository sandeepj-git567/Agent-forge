"""
Tests for Task API Endpoints
"""
from fastapi.testclient import TestClient

from agentforge.api.main import app

client = TestClient(app)


def test_post_task_run_success():
    payload = {
        "task": "Research enterprise AI agent frameworks",
        "mode": "research"
    }
    response = client.post("/api/v1/tasks/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "run_id" in data
    assert "result" in data
    assert "trace" in data
    assert data["errors"] == []


def test_post_task_run_dangerous_rejected():
    payload = {
        "task": "drop table users; --",
        "mode": "malicious"
    }
    response = client.post("/api/v1/tasks/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert len(data["errors"]) > 0


def test_get_task_trace_not_found():
    response = client.get("/api/v1/tasks/non_existent_run_id_999")
    assert response.status_code == 404


def test_cancel_task_endpoint():
    response = client.post("/api/v1/tasks/run_123_test/cancel")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "cancellation request recorded" in data["message"]

