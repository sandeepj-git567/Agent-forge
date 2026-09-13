"""
Framework Abstraction Engine for AgentForge AI

Provides a unified interface allowing side-by-side comparison between
Google ADK (Primary) and CrewAI (Comparison Adapter).
"""
from abc import ABC, abstractmethod
from typing import Any


class BaseAgentFrameworkAdapter(ABC):
    """Abstract Base Class for Agent Framework Adapters."""

    @property
    @abstractmethod
    def framework_name(self) -> str:
        """Name of the underlying agent framework."""

    @property
    @abstractmethod
    def is_primary(self) -> bool:
        """True if this is the primary agent framework."""

    @abstractmethod
    async def execute_task(self, task: str, mode: str = "general") -> dict[str, Any]:
        """Execute task using the underlying framework."""
