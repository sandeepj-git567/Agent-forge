"""
Task Orchestration and Trace Retrieval Router
"""
from fastapi import APIRouter, HTTPException, status

from agentforge.api.schemas import TaskRunRequest, TaskRunResponse
from agentforge.runtime.executor import default_agent_executor
from agentforge.runtime.tracer import get_trace

router = APIRouter(prefix="/tasks", tags=["Task Orchestration"])


@router.post("/run", response_model=TaskRunResponse)
async def run_task(payload: TaskRunRequest) -> TaskRunResponse:
    """
    Submit and execute an AI agent task through AgentForge AI orchestration.
    """
    result = await default_agent_executor.run_task(
        task=payload.task,
        mode=payload.mode,
        has_approval=payload.has_approval,
        allowlist=payload.allowlist
    )
    return TaskRunResponse(**result)


@router.get("/{run_id}", response_model=TaskRunResponse)
async def get_task_trace(run_id: str) -> TaskRunResponse:
    """
    Retrieve execution trace and status by run_id.
    """
    trace = get_trace(run_id)
    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution run ID '{run_id}' not found."
        )

    return TaskRunResponse(
        run_id=trace.run_id,
        status=trace.status,
        result=trace.final_output,
        errors=trace.errors,
        trace=trace.model_dump()
    )
