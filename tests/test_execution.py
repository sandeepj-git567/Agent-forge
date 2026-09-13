"""
Tests for Agent Runtime Execution, Tracing, and API Key Fallbacks
"""
import pytest

from agentforge.runtime.executor import AgentExecutor
from agentforge.runtime.tracer import get_trace


@pytest.mark.asyncio
async def test_execution_with_valid_task():
    executor = AgentExecutor()
    task = "Research AI agent orchestration design patterns"
    response = await executor.run_task(task, mode="research")

    assert response["status"] == "completed"
    assert response["run_id"] is not None
    assert response["result"] is not None
    assert len(response["errors"]) == 0

    trace_data = response["trace"]
    assert trace_data["task"] == task
    assert len(trace_data["events"]) >= 3


@pytest.mark.asyncio
async def test_execution_trace_retrieval():
    executor = AgentExecutor()
    response = await executor.run_task("Evaluate agent tool permissions", mode="eval")
    run_id = response["run_id"]

    saved_trace = get_trace(run_id)
    assert saved_trace is not None
    assert saved_trace.run_id == run_id
    assert saved_trace.status == "completed"


@pytest.mark.asyncio
async def test_execution_guardrail_rejection():
    executor = AgentExecutor()
    response = await executor.run_task("rm -rf /", mode="dangerous")
    assert response["status"] == "failed"
    assert len(response["errors"]) > 0
    assert "dangerous request" in response["errors"][0].lower()
