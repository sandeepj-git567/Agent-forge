"""
Executable Workflow Engine Management and Execution API Router
"""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agentforge.auth.dependencies import get_current_user_optional
from agentforge.db.models import User
from agentforge.db.repositories.workflow_repository import WorkflowRepository
from agentforge.db.session import get_db
from agentforge.workflows.builder import default_workflow_generator
from agentforge.workflows.engine import default_workflow_engine

router = APIRouter(prefix="/workflows", tags=["Workflow Management & Executable Engine"])


class WorkflowCreateRequest(BaseModel):
    """Payload for creating a new workflow definition."""
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Description of workflow goal")
    graph_definition: dict[str, Any] | None = Field(default=None, description="Optional custom DAG graph definition")


class WorkflowExecuteRequest(BaseModel):
    """Payload for executing a workflow."""
    inputs: dict[str, Any] = Field(default_factory=dict, description="Input parameters for execution")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    payload: WorkflowCreateRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
) -> dict[str, Any]:
    """Create and persist a new DAG workflow definition in database."""
    repo = WorkflowRepository(db)
    
    if payload.graph_definition:
        graph_def = payload.graph_definition
    else:
        generated = default_workflow_generator.generate_workflow_definition(payload.description)
        # Convert generated steps to nodes format for DAG execution engine
        graph_def = {
            "nodes": [
                {
                    "id": f"node-{idx+1}",
                    "agent": step.get("agent", "planner"),
                    "action": step.get("action", "Execute step"),
                    "depends_on": [f"node-{idx}"] if idx > 0 else []
                }
                for idx, step in enumerate(generated.get("steps", []))
            ],
            "visualizations": generated.get("visualizations", {})
        }

    owner_id = current_user.id if current_user else None
    wf = repo.create_workflow(
        name=payload.name,
        description=payload.description,
        graph_definition=graph_def,
        owner_id=owner_id
    )

    return {
        "id": wf.id,
        "name": wf.name,
        "description": wf.description,
        "graph_definition": wf.graph_definition,
        "created_at": wf.created_at.isoformat() if wf.created_at else None
    }


@router.get("", response_model=list[dict[str, Any]])
async def list_workflows(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """List all saved workflows from database."""
    repo = WorkflowRepository(db)
    workflows = repo.list_workflows()
    return [
        {
            "id": wf.id,
            "name": wf.name,
            "description": wf.description,
            "graph_definition": wf.graph_definition,
            "created_at": wf.created_at.isoformat() if wf.created_at else None
        }
        for wf in workflows
    ]


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Retrieve single workflow definition by ID from database."""
    repo = WorkflowRepository(db)
    wf = repo.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow ID '{workflow_id}' not found.")
    return {
        "id": wf.id,
        "name": wf.name,
        "description": wf.description,
        "graph_definition": wf.graph_definition,
        "created_at": wf.created_at.isoformat() if wf.created_at else None
    }


@router.get("/{workflow_id}/visualize")
async def visualize_workflow(workflow_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Get Mermaid and ASCII visualization diagrams for workflow."""
    repo = WorkflowRepository(db)
    wf = repo.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow ID '{workflow_id}' not found.")

    viz = wf.graph_definition.get("visualizations") if isinstance(wf.graph_definition, dict) else None
    if not viz:
        viz = default_workflow_generator.generate_workflow_definition(wf.description or wf.name).get("visualizations", {})

    return {
        "workflow_id": workflow_id,
        "name": wf.name,
        "visualizations": viz
    }


@router.post("/{workflow_id}/execute", status_code=status.HTTP_202_ACCEPTED)
async def execute_workflow(
    workflow_id: str,
    payload: WorkflowExecuteRequest = WorkflowExecuteRequest(),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
) -> dict[str, Any]:
    """
    Trigger execution of a DAG workflow graph.
    Executes independent nodes in parallel waves and tracks execution in database.
    """
    repo = WorkflowRepository(db)
    wf = repo.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow ID '{workflow_id}' not found.")

    user_id = current_user.id if current_user else None
    execution = repo.create_execution(workflow_id=wf.id, inputs=payload.inputs, user_id=user_id)

    res = await default_workflow_engine.execute_workflow(
        execution_id=execution.id,
        graph_definition=wf.graph_definition,
        db=db,
        inputs=payload.inputs
    )

    return {
        "execution_id": execution.id,
        "workflow_id": wf.id,
        "status": res.get("status"),
        "node_states": res.get("node_states"),
        "approval_id": res.get("approval_id"),
        "error": res.get("error")
    }


@router.get("/executions/{execution_id}")
async def get_execution_status(execution_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Retrieve detailed workflow execution trace log and node states from database."""
    repo = WorkflowRepository(db)
    ex = repo.get_execution(execution_id)
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow execution ID '{execution_id}' not found.")

    return {
        "execution_id": ex.id,
        "workflow_id": ex.workflow_id,
        "status": ex.status,
        "node_states": ex.node_states,
        "inputs": ex.inputs,
        "outputs": ex.outputs,
        "error_details": ex.error_details,
        "start_time": ex.start_time.isoformat() if ex.start_time else None,
        "end_time": ex.end_time.isoformat() if ex.end_time else None
    }


@router.post("/approvals/{approval_id}/approve")
async def approve_workflow_checkpoint(
    approval_id: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
) -> dict[str, Any]:
    """Approve a human checkpoint, resuming workflow execution."""
    approver = current_user.email if current_user else "admin"
    res = await default_workflow_engine.resume_workflow(approval_id=approval_id, approve=True, db=db, approver_email=approver)
    return res


@router.post("/approvals/{approval_id}/reject")
async def reject_workflow_checkpoint(
    approval_id: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
) -> dict[str, Any]:
    """Reject a human checkpoint, cancelling workflow execution."""
    approver = current_user.email if current_user else "admin"
    res = await default_workflow_engine.resume_workflow(approval_id=approval_id, approve=False, db=db, approver_email=approver)
    return res
