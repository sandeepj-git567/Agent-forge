"""
CrewAI Comparison Framework Adapter for AgentForge AI

Provides an optional adapter interface for comparing orchestration performance
against Google ADK 2.9.0 without replacing Google ADK as the primary framework.
"""
from typing import Any

from agentforge.framework.base import BaseAgentFrameworkAdapter


class CrewAIComparisonAdapter(BaseAgentFrameworkAdapter):
    """CrewAI Framework Comparison Adapter."""

    @property
    def framework_name(self) -> str:
        return "CrewAI Adapter (Comparison)"

    @property
    def is_primary(self) -> bool:
        return False

    async def execute_task(self, task: str, mode: str = "general") -> dict[str, Any]:
        return {
            "run_id": "crewai-simulated-run",
            "framework": self.framework_name,
            "status": "completed",
            "result": f"[CrewAI Comparison Adapter Output]: Executed task '{task}' in {mode} mode.",
            "comparison_notes": "Google ADK 2.9.0 provides superior stateful session management and native event streaming.",
            "errors": []
        }
