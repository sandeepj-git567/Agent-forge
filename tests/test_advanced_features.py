"""
Tests for Advanced Multi-Agent Workflows, Evaluation Engine, Framework Adapters, and Auth
"""
import pytest
from fastapi.testclient import TestClient

from agentforge.agents.classifier import default_intent_classifier
from agentforge.api.main import app
from agentforge.auth.jwt import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from agentforge.auth.roles import UserRole, has_sufficient_role
from agentforge.eval.evaluator import default_evaluator
from agentforge.framework.crewai_adapter import CrewAIComparisonAdapter
from agentforge.framework.google_adk_adapter import GoogleADKFrameworkAdapter
from agentforge.workflows.builder import default_workflow_generator
from agentforge.workflows.task_graph import default_workflow_builder

client = TestClient(app)


def test_intent_classifier():
    res_code = default_intent_classifier.classify_intent("Write a python script for sorting")
    assert res_code["mode"] == "coding"
    assert "coder" in res_code["recommended_agents"]

    res_research = default_intent_classifier.classify_intent("Research quantum computing papers")
    assert res_research["mode"] == "research"


def test_task_graph_builder():
    graph = default_workflow_builder.build_graph_for_mode("TestCodingWf", "coding")
    assert graph.workflow_name == "TestCodingWf"
    assert len(graph.steps) == 3

    exec_steps = graph.get_executable_steps()
    assert len(exec_steps) == 1
    assert exec_steps[0].id == "plan"


def test_workflow_generator_diagrams():
    wf_data = default_workflow_generator.generate_workflow_definition("Research AI architectures")
    assert "graph TD" in wf_data["visualizations"]["mermaid"]
    assert "[USER GOAL]" in wf_data["visualizations"]["ascii"]


def test_ai_evaluator():
    res = default_evaluator.evaluate_response("What is AgentForge?", "AgentForge AI is a platform based on Google ADK 2.9.0.")
    assert res.overall_score >= 0.7
    assert res.correctness_score > 0.0


@pytest.mark.asyncio
async def test_framework_adapters():
    adk_adapter = GoogleADKFrameworkAdapter()
    assert adk_adapter.is_primary is True
    res_adk = await adk_adapter.execute_task("Simple task")
    assert res_adk["status"] == "completed"

    crew_adapter = CrewAIComparisonAdapter()
    assert crew_adapter.is_primary is False
    res_crew = await crew_adapter.execute_task("Simple task")
    assert res_crew["status"] == "completed"


def test_jwt_auth_and_roles():
    hashed = hash_password("secret_pass123")
    assert verify_password("secret_pass123", hashed) is True

    token = create_access_token({"sub": "dev@agentforge.ai", "role": "ADMIN"})
    decoded = decode_access_token(token)
    assert decoded["sub"] == "dev@agentforge.ai"
    assert decoded["role"] == "ADMIN"

    assert has_sufficient_role("ADMIN", UserRole.USER) is True
    assert has_sufficient_role("VIEWER", UserRole.ENGINEER) is False


def test_auth_api_endpoints():
    reg_body = {"email": "new_user@agentforge.ai", "password": "securepassword123", "role": "USER"}
    res_reg = client.post("/api/v1/auth/register", json=reg_body)
    assert res_reg.status_code == 201
    assert "access_token" in res_reg.json()

    login_body = {"email": "new_user@agentforge.ai", "password": "securepassword123"}
    res_login = client.post("/api/v1/auth/login", json=login_body)
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()


def test_workflow_api_endpoints():
    wf_body = {"name": "Research Workflow", "description": "Research quantum AI agent models"}
    res_create = client.post("/api/v1/workflows", json=wf_body)
    assert res_create.status_code == 201
    wf_id = res_create.json()["id"]

    res_get = client.get(f"/api/v1/workflows/{wf_id}")
    assert res_get.status_code == 200

    res_viz = client.get(f"/api/v1/workflows/{wf_id}/visualize")
    assert res_viz.status_code == 200
    assert "mermaid" in res_viz.json()["visualizations"]


def test_evaluations_api_endpoints():
    eval_body = {
        "input_text": "Describe AgentForge AI",
        "actual_output": "AgentForge AI is an enterprise AI agent platform."
    }
    res_eval = client.post("/api/v1/evaluations/run", json=eval_body)
    assert res_eval.status_code == 201
    assert "overall_score" in res_eval.json()

    res_bench = client.get("/api/v1/evaluations/benchmarks")
    assert res_bench.status_code == 200
    assert res_bench.json()["count"] > 0


def test_observability_middleware_headers():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "x-correlation-id" in response.headers
    assert "x-process-time-ms" in response.headers
