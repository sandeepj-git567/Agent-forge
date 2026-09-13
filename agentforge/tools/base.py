"""
Base Tool Abstractions and Permission Classifications for AgentForge AI
"""
from collections.abc import Callable
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PermissionCategory(str, Enum):
    """Tool Permission Categories"""
    READ_ONLY = "READ_ONLY"
    EXTERNAL_SEARCH = "EXTERNAL_SEARCH"
    FILE_ANALYSIS = "FILE_ANALYSIS"
    WRITE = "WRITE"
    DESTRUCTIVE = "DESTRUCTIVE"


class ToolDefinition(BaseModel):
    """Metadata and execution container for registered tools"""
    name: str = Field(..., description="Unique tool identifier name")
    description: str = Field(..., description="Description of tool functionality")
    permission_category: PermissionCategory = Field(..., description="Required permission category")
    input_schema: dict[str, Any] = Field(default_factory=dict, description="JSON Schema for inputs")
    output_schema: dict[str, Any] = Field(default_factory=dict, description="JSON Schema for outputs")
    func: Callable[..., Any] = Field(..., exclude=True, description="Python callable execution function")
    requires_approval: bool = Field(default=False, description="Whether execution requires human approval")

    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool function with kwargs."""
        return self.func(**kwargs)
