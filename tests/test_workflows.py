"""
Comprehensive Tests for Executable DAG Workflow Engine (Stage 7)
"""
import pytest
from fastapi.testclient import TestClient

from agentforge.api.main import app
from agentforge.workflows.engine import CyclicDependencyError, default_workflow_engine

client = TestClient(app)


def test_dag_cycle_detection_and_waves():
    # Valid DAG: Node A -> Node B & C -> Node D
    nodes_valid = [
        {"id": "node-A", "depends_on": []},
        {"id": "node-B", "depends_on": ["node-A"]},
        {"id": "node-C", "depends_on": ["node-A"]},
        {"id": "node-D", "depends_on": ["node-B", "node-C"]}
    ]
    waves = default_workflow_engine.detect_cycles_and_sort(nodes_valid)
    assert len(waves) == 3
    assert waves[0] == ["node-A"]
    assert set(waves[1]) == {"node-B", "node-C"}
    assert waves[2] == ["node-D"]

    # Cyclic DAG: Node A -> Node B -> Node A
    nodes_cyclic = [
        {"id": "node-A", "depends_on": ["node-B"]},
        {"id": "node-B", "depends_on": ["node-A"]}
    ]
    with pytest.raises(CyclicDependencyError, match="circular/cyclic dependencies"):
        default_workflow_engine.detect_cycles_and_sort(nodes_cyclic)


def test_workflow_create_get_list_api():
    # 1. Create Workflow
    wf_payload = {
        "name": "Stage 7 Test Workflow",
        "description": "Automated pipeline for research and reporting"
    }
    create_res = client.post("/api/v1/workflows", json=wf_payload)
    assert create_res.status_code == 201
    wf_data = create_res.json()
    wf_id = wf_data["id"]
    assert wf_id is not None
    assert "nodes" in wf_data["graph_definition"]

    # 2. Get Workflow
    get_res = client.get(f"/api/v1/workflows/{wf_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == wf_id

    # 3. List Workflows
    list_res = client.get("/api/v1/workflows")
    assert list_res.status_code == 200
    assert any(w["id"] == wf_id for w in list_res.json())


@pytest.mark.asyncio
async def test_workflow_execution_api():
    # Create custom executable DAG workflow
    wf_payload = {
        "name": "Executable DAG Test",
        "description": "Test execution of DAG steps",
        "graph_definition": {
            "nodes": [
                {"id": "step-1", "action": "Generate search plan", "agent": "planner"},
                {"id": "step-2", "action": "Perform web search", "tool": "web_search", "tool_kwargs": {"query": "Google ADK"}, "depends_on": ["step-1"]}
            ]
        }
    }
    create_res = client.post("/api/v1/workflows", json=wf_payload)
    wf_id = create_res.json()["id"]

    # Execute workflow
    exec_res = client.post(f"/api/v1/workflows/{wf_id}/execute")
    assert exec_res.status_code == 202
    exec_data = exec_res.json()
    exec_id = exec_data["execution_id"]
    assert exec_data["status"] == "completed"
    assert "step-1" in exec_data["node_states"]
    assert "step-2" in exec_data["node_states"]

    # Fetch execution status
    status_res = client.get(f"/api/v1/workflows/executions/{exec_id}")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_workflow_approval_checkpoint_pause_and_resume():
    # Create workflow with human approval checkpoint
    wf_payload = {
        "name": "Approval Workflow",
        "description": "Workflow requiring human approval checkpoint",
        "graph_definition": {
            "nodes": [
                {"id": "step-1", "action": "Prepare database update", "agent": "planner"},
                {"id": "step-2", "action": "Execute dangerous write", "tool": "task_management", "tool_kwargs": {"action": "create", "task_id": "t1", "title": "test"}, "requires_approval": True, "depends_on": ["step-1"]}
            ]
        }
    }
    create_res = client.post("/api/v1/workflows", json=wf_payload)
    wf_id = create_res.json()["id"]

    # Execute workflow -> should pause at step-2 for approval
    exec_res = client.post(f"/api/v1/workflows/{wf_id}/execute")
    assert exec_res.status_code == 202
    exec_data = exec_res.json()
    assert exec_data["status"] == "paused_approval"
    approval_id = exec_data["approval_id"]
    assert approval_id is not None

    # Approve checkpoint
    app_res = client.post(f"/api/v1/workflows/approvals/{approval_id}/approve")
    assert app_res.status_code == 200
    assert app_res.json()["status"] == "completed"
