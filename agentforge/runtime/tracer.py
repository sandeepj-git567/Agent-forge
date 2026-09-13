"""
Execution Trace Recorder for AgentForge AI

Maintains safe, audit-compliant execution traces without storing secret keys,
passwords, or private chain-of-thought rationale.
"""
import time
import uuid
from typing import Any

from pydantic import BaseModel, Field

from agentforge.guardrails.output_guard import default_output_guard


class TraceEvent(BaseModel):
    """Single execution event entry in trace timeline."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent: str = Field(..., description="Agent name producing event")
    event_type: str = Field(..., description="Type of event e.g. agent_start, tool_call, validation, completed")
    tool: str | None = Field(default=None, description="Tool name if event involves tool")
    start_time: float = Field(default_factory=time.time)
    end_time: float | None = Field(default=None)
    status: str = Field(default="in_progress")
    safe_metadata: dict[str, Any] = Field(default_factory=dict, description="Sanitized metadata")
    error: str | None = Field(default=None)

    def complete(self, status: str = "completed", error: str | None = None, extra_metadata: dict[str, Any] | None = None) -> None:
        self.end_time = time.time()
        self.status = status
        self.error = error
        if extra_metadata:
            self.safe_metadata.update(default_output_guard.sanitize_dict(extra_metadata))


class ExecutionTrace(BaseModel):
    """Complete execution trace container for a single task run."""
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task: str = Field(..., description="Sanitized user task input")
    mode: str = Field(default="general", description="Task execution mode")
    status: str = Field(default="pending")
    start_time: float = Field(default_factory=time.time)
    end_time: float | None = Field(default=None)
    events: list[TraceEvent] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    final_output: str | None = Field(default=None)

    def add_event(self, agent: str, event_type: str, tool: str | None = None, safe_metadata: dict[str, Any] | None = None) -> TraceEvent:
        clean_metadata = default_output_guard.sanitize_dict(safe_metadata or {})
        event = TraceEvent(
            agent=agent,
            event_type=event_type,
            tool=tool,
            safe_metadata=clean_metadata
        )
        self.events.append(event)
        return event

    def finish(self, status: str, final_output: str | None = None, errors: list[str] | None = None) -> None:
        self.end_time = time.time()
        self.status = status
        if final_output:
            self.final_output = default_output_guard.sanitize_text(final_output)
        if errors:
            self.errors.extend([default_output_guard.sanitize_text(e) for e in errors])


# Global in-memory storage for traces (Phase 1)
_TRACE_STORE: dict[str, ExecutionTrace] = {}


def save_trace(trace: ExecutionTrace) -> None:
    _TRACE_STORE[trace.run_id] = trace


def get_trace(run_id: str) -> ExecutionTrace | None:
    return _TRACE_STORE.get(run_id)
