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

    agents_used = list({e.agent for e in trace.events})
    tools_used = [e.tool for e in trace.events if e.tool]

    return TaskRunResponse(
        run_id=trace.run_id,
        status=trace.status,
        answer=trace.final_output,
        result=trace.final_output,
        agents_used=agents_used,
        tools_used=tools_used,
        errors=trace.errors,
        trace=trace.model_dump()
    )


@router.post("/{run_id}/cancel")
async def cancel_task_run(run_id: str) -> dict:
    """
    Cancel an active task execution run by ID.
    """
    cancelled = default_agent_executor.cancel_task(run_id)
    return {
        "status": "success" if cancelled else "not_running",
        "message": f"Task execution run '{run_id}' cancellation request recorded."
    }

