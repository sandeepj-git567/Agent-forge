"""
Google ADK 2.9.0 Primary Framework Adapter for AgentForge AI
"""
from typing import Any

from agentforge.framework.base import BaseAgentFrameworkAdapter
from agentforge.runtime.executor import default_agent_executor


class GoogleADKFrameworkAdapter(BaseAgentFrameworkAdapter):
    """Google ADK 2.9.0 Primary Agent Framework Adapter."""

    @property
    def framework_name(self) -> str:
        return "Google ADK 2.9.0"

    @property
    def is_primary(self) -> bool:
        return True

    async def execute_task(self, task: str, mode: str = "general") -> dict[str, Any]:
        result = await default_agent_executor.run_task(task=task, mode=mode)
        result["framework"] = self.framework_name
        return result
