"""
Permission Guardrails and Policy Verification for AgentForge AI
"""
from typing import Any

from agentforge.tools.base import PermissionCategory
from agentforge.tools.registry import ToolRegistry, default_tool_registry


class PermissionGuard:
    """Verifies tool permissions and approval flags before execution."""

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or default_tool_registry

    def check_tool_permission(
        self,
        tool_name: str,
        has_human_approval: bool = False,
        allowed_tools: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Validate if tool execution is authorized under safety policies.
        """
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return {
                "allowed": False,
                "reason": f"Tool '{tool_name}' not recognized in registry.",
                "requires_approval": False
            }

        if allowed_tools is not None and tool_name not in allowed_tools:
            return {
                "allowed": False,
                "reason": f"Tool '{tool_name}' is not in the allowed tools list.",
                "requires_approval": False
            }

        if tool.permission_category == PermissionCategory.DESTRUCTIVE and not has_human_approval:
            return {
                "allowed": False,
                "reason": "Destructive operations are strictly blocked without human approval.",
                "requires_approval": True
            }

        return {
            "allowed": True,
            "reason": "Permission check passed.",
            "requires_approval": tool.requires_approval
        }


default_permission_guard = PermissionGuard()
