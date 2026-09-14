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
    assert "workflow_planning" in tool_names


def test_web_search_tool():
    res = web_search("agent framework")
    assert res["status"] == "success"
    assert len(res["results"]) > 0


def test_doc_search_tool():
    from agentforge.rag.chunker import TextChunk
    from agentforge.rag.store import default_vector_store

    chunk = TextChunk(chunk_index=0, content="AgentForge AI is an enterprise agent framework.", chunk_hash="h1")
    default_vector_store.add_document("doc-test-1", "test.txt", [chunk])

    res = document_search("AgentForge")
    assert res["status"] in ("success", "insufficient_evidence")
    assert "query" in res


def test_workflow_planning_tool():
    from agentforge.tools.workflow_planning import workflow_planning
    res = workflow_planning(goal="Build a web scraper and index in RAG", max_steps=3)
    assert res["status"] == "success"
    assert res["step_count"] == 3
    assert res["is_executable"] is True


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
    assert "DESTRUCTIVE" in result["error"] or "requires explicit approval" in result["error"]


def test_ssrf_guardrail_blocking():
    def fetch_url(url: str):
        return {"url": url, "content": "fetched"}

    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="fetch_url",
            description="Fetches URL content",
            permission_category=PermissionCategory.EXTERNAL_SEARCH,
            func=fetch_url
        )
    )

    # Private IP or localhost target should be blocked by SSRF Guardrail
    res_local = registry.execute_tool("fetch_url", {"url": "http://127.0.0.1/admin"})
    assert res_local["status"] == "blocked"
    assert "SSRF Security Guardrail" in res_local["error"]

    res_aws = registry.execute_tool("fetch_url", {"url": "http://169.254.169.254/latest/meta-data"})
    assert res_aws["status"] == "blocked"
    assert "SSRF Security Guardrail" in res_aws["error"]


def test_output_secret_redaction():
    def dummy_key_exposer():
        return {
            "api_key": "AIzaSyD-TestKey12345678901234567890123",
            "password": "supersecretpassword123",
            "bearer_token": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        }

    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="expose_key",
            description="Exposes key for testing",
            permission_category=PermissionCategory.READ_ONLY,
            func=dummy_key_exposer
        )
    )

    res = registry.execute_tool("expose_key", {})
    assert res["status"] == "success"
    val = res["result"]
    assert val["api_key"] == "[REDACTED_SECRET]"
    assert val["password"] == "[REDACTED_SECRET]"

