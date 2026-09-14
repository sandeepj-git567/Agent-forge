"""
FastAPI Request and Response Pydantic Schemas for AgentForge AI
"""
from typing import Any

from pydantic import BaseModel, Field

from agentforge.config.settings import settings


class TaskRunRequest(BaseModel):

    """Payload for POST /api/v1/tasks/run"""
    task: str = Field(..., description="User task description to process", json_schema_extra={"example": "Research enterprise AI agent frameworks"})
    mode: str = Field(default="general", description="Task execution mode", json_schema_extra={"example": "research"})
    has_approval: bool = Field(default=False, description="Explicit approval for sensitive actions")
    allowlist: list[str] | None = Field(default=None, description="Optional list of permitted tool names")


class TaskRunResponse(BaseModel):
    """Response payload for POST /api/v1/tasks/run"""
    run_id: str = Field(..., description="Unique execution run ID")
    status: str = Field(..., description="Execution status e.g. completed, failed, cancelled")
    answer: str | None = Field(default=None, description="Synthesized agent answer")
    result: str | None = Field(default=None, description="Validated agent execution response")
    agents_used: list[str] = Field(default_factory=list, description="List of sub-agent names invoked")
    tools_used: list[str] = Field(default_factory=list, description="List of tool names executed")
    latency_ms: float = Field(default=0.0, description="Execution latency in milliseconds")
    model: str = Field(default=settings.GOOGLE_MODEL, description="LLM Model used")
    execution_mode: str = Field(default="local_development", description="Execution mode: gemini, local_development, or failed")
    errors: list[str] = Field(default_factory=list, description="List of execution or guardrail errors")
    trace: dict[str, Any] = Field(default_factory=dict, description="Complete execution trace")



class HealthResponse(BaseModel):
    """Response payload for GET /api/v1/health"""
    status: str = Field(default="healthy")
    version: str = Field(default="1.0.0")
    environment: str = Field(default="development")


class ReadinessResponse(BaseModel):
    """Response payload for GET /api/v1/health/ready"""
    status: str = Field(default="ready")
    services: dict[str, str] = Field(default_factory=dict)
