"""
Tests for Health and Readiness Endpoints
"""
from fastapi.testclient import TestClient

from agentforge.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


def test_readiness_endpoint():
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "services" in data
    assert "tools_registry" in data["services"]


def test_config_endpoint():
    response = client.get("/api/v1/health/config")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "AgentForge AI"
    assert "providers" in data
    # Ensure sensitive fields are never exposed
    assert "JWT_SECRET" not in data
    assert "GOOGLE_API_KEY" not in data
    assert "DATABASE_URL" not in data


def test_metrics_endpoint():
    response = client.get("/api/v1/health/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "total_errors" in data
    assert "avg_latency_ms" in data
    assert "X-Correlation-ID" in response.headers
    assert "X-Process-Time-MS" in response.headers


