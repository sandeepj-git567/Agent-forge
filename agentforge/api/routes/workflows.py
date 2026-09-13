"""
Workflow Management and Visual Builder API Router
"""
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from agentforge.workflows.builder import default_workflow_generator

router = APIRouter(prefix="/workflows", tags=["Workflow Management & Builder"])

_WORKFLOW_STORE: dict[str, dict[str, Any]] = {}


class WorkflowCreateRequest(BaseModel):
    """Payload for creating a new workflow."""
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Description of workflow goal")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workflow(payload: WorkflowCreateRequest) -> dict[str, Any]:
    """Generate workflow definition from natural language description."""
    wf_def = default_workflow_generator.generate_workflow_definition(payload.description)
    wf_id = f"wf-{uuid.uuid4().hex[:8]}"

    workflow_record = {
        "id": wf_id,
        "name": payload.name,
        **wf_def
    }
    _WORKFLOW_STORE[wf_id] = workflow_record
    return workflow_record


@router.get("", response_model=list[dict[str, Any]])
async def list_workflows() -> list[dict[str, Any]]:
    """List all saved workflows."""
    return list(_WORKFLOW_STORE.values())


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str) -> dict[str, Any]:
    """Retrieve single workflow definition by ID."""
    if workflow_id not in _WORKFLOW_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow ID '{workflow_id}' not found.")
    return _WORKFLOW_STORE[workflow_id]


@router.get("/{workflow_id}/visualize")
async def visualize_workflow(workflow_id: str) -> dict[str, Any]:
    """Get Mermaid and ASCII visualization diagrams for workflow."""
    if workflow_id not in _WORKFLOW_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow ID '{workflow_id}' not found.")

    wf = _WORKFLOW_STORE[workflow_id]
    return {
        "workflow_id": workflow_id,
        "name": wf["name"],
        "visualizations": wf["visualizations"]
    }
