"""
Tests for Core Tools and Tool Registry
"""
from agentforge.tools.base import PermissionCategory, ToolDefinition
from agentforge.tools.code_analysis import safe_code_analysis
from agentforge.tools.doc_search import document_search
from agentforge.tools.registry import ToolRegistry, default_tool_registry
from agentforge.tools.web_search import web_search


def test_tool_registry_list():
    tools = default_tool_registry.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "web_search" in tool_names
    assert "document_search" in tool_names
    assert "safe_code_analysis" in tool_names
    assert "task_management" in tool_names


def test_web_search_tool():
    res = web_search("agent framework")
    assert res["status"] == "success"
    assert len(res["results"]) > 0


def test_doc_search_tool():
    res = document_search("AgentForge")
    assert res["status"] == "success"
    assert res["count"] > 0


def test_safe_code_analysis_tool():
    code = "def hello():\n    return 'world'"
    res = safe_code_analysis(code)
    assert res["status"] == "success"
    assert res["valid_syntax"] is True
    assert res["metrics"]["functions"] == ["hello"]
    assert res["is_secure"] is True


def test_safe_code_analysis_dangerous_call():
    code = "import os\nos.system('dir')"
    res = safe_code_analysis(code)
    assert res["status"] == "success"
    assert len(res["security_warnings"]) > 0
    assert res["is_secure"] is False


def test_destructive_tool_blocked_by_registry():
    registry = ToolRegistry()
    
    def dummy_destructive():
        return "deleted"

    registry.register(
        ToolDefinition(
            name="delete_database",
            description="Deletes database",
            permission_category=PermissionCategory.DESTRUCTIVE,
            func=dummy_destructive,
            requires_approval=True
        )
    )

    # Executing without approval must return 'blocked'
    result = registry.execute_tool("delete_database", {}, has_approval=False)
    assert result["status"] == "blocked"
    assert "DESTRUCTIVE" in result["error"]
