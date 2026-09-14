"""
Central Tool Registry and Authorization Engine for AgentForge AI
"""
from typing import Any

from agentforge.guardrails.input_guard import redact_secrets, validate_url_ssrf
from agentforge.tools.base import PermissionCategory, ToolDefinition
from agentforge.tools.code_analysis import safe_code_analysis
from agentforge.tools.doc_search import document_search
from agentforge.tools.task_manager import task_management
from agentforge.tools.web_search import web_search
from agentforge.tools.workflow_planning import workflow_planning


class ToolRegistry:
    """Central registry managing tool definitions and execution permission checks."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def register(self, tool_def: ToolDefinition) -> None:
        """Register a new tool definition."""
        self._tools[tool_def.name] = tool_def

    def get_tool(self, name: str) -> ToolDefinition | None:
        """Get registered tool definition by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        """List metadata for all registered tools."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "permission_category": t.permission_category.value,
                "requires_approval": t.requires_approval
            }
            for t in self._tools.values()
        ]

    def execute_tool(
        self,
        name: str,
        kwargs: dict[str, Any],
        has_approval: bool = False,
        allowlist: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Execute tool with permission checks, SSRF URL validation, approval guards, and output secret redaction.
        """
        tool = self.get_tool(name)
        if not tool:
            return {"status": "error", "error": f"Tool '{name}' is not registered in ToolRegistry."}

        # Allowlist check
        if allowlist is not None and name not in allowlist:
            return {"status": "error", "error": f"Tool '{name}' is not permitted by execution allowlist."}

        # Permission check: Destructive action or required approval blocking
        if (tool.permission_category == PermissionCategory.DESTRUCTIVE or tool.requires_approval) and not has_approval:
            return {
                "status": "blocked",
                "error": f"Tool '{name}' requires explicit approval for operations in category '{tool.permission_category.value}'."
            }

        # SSRF URL Validation Guardrail
        for k, v in kwargs.items():
            if isinstance(v, str) and (v.startswith("http://") or v.startswith("https://") or "url" in k.lower()):
                is_valid_url, ssrf_err = validate_url_ssrf(v)
                if not is_valid_url:
                    return {
                        "status": "blocked",
                        "error": f"Tool execution blocked by SSRF Security Guardrail: {ssrf_err}"
                    }

        try:
            raw_result = tool.execute(**kwargs)
            sanitized_result = redact_secrets(raw_result)
            return {"status": "success", "result": sanitized_result}
        except Exception as err:  # noqa: BLE001
            return {"status": "error", "error": f"Tool '{name}' execution failed: {err!s}"}

    def _register_default_tools(self) -> None:
        """Register Phase 1 core tools."""
        self.register(
            ToolDefinition(
                name="web_search",
                description="Search external web sources for up-to-date information.",
                permission_category=PermissionCategory.EXTERNAL_SEARCH,
                input_schema={"query": "string", "max_results": "integer"},
                output_schema={"status": "string", "results": "array"},
                func=web_search
            )
        )
        self.register(
            ToolDefinition(
                name="document_search",
                description="Search internal knowledge base documents.",
                permission_category=PermissionCategory.READ_ONLY,
                input_schema={"query": "string", "category": "string"},
                output_schema={"status": "string", "documents": "array"},
                func=document_search
            )
        )
        self.register(
            ToolDefinition(
                name="safe_code_analysis",
                description="Perform static AST analysis and security audit on Python code without execution.",
                permission_category=PermissionCategory.FILE_ANALYSIS,
                input_schema={"code": "string"},
                output_schema={"status": "string", "security_warnings": "array"},
                func=safe_code_analysis
            )
        )
        self.register(
            ToolDefinition(
                name="task_management",
                description="Create and update workflow tasks in memory.",
                permission_category=PermissionCategory.WRITE,
                input_schema={"action": "string", "task_id": "string", "title": "string"},
                output_schema={"status": "string", "task": "object"},
                func=task_management
            )
        )
        self.register(
            ToolDefinition(
                name="workflow_planning",
                description="Generate structured workflow graph plan from target goal.",
                permission_category=PermissionCategory.WRITE,
                input_schema={"goal": "string", "max_steps": "integer"},
                output_schema={"status": "string", "steps": "array"},
                func=workflow_planning
            )
        )


# Global singleton registry instance
default_tool_registry = ToolRegistry()
