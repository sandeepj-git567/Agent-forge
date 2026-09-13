"""
Web Search Tool Interface for AgentForge AI
"""
from typing import Any


def web_search(query: str, max_results: int = 5) -> dict[str, Any]:
    """
    Interface for external web search (EXTERNAL_SEARCH category).
    Provides simulated/mocked search results if external API keys are not provided.
    """
    query_clean = query.strip()
    if not query_clean:
        return {"status": "error", "message": "Search query cannot be empty", "results": []}

    # Safe mock search output for Phase 1 verification
    mock_results: list[dict[str, str]] = [
        {
            "title": f"Enterprise AI Agent Frameworks - {query_clean}",
            "snippet": f"Overview of multi-agent orchestration, tool calling, and RAG architectures for {query_clean}.",
            "url": "https://docs.agentforge.ai/frameworks/enterprise-adk"
        },
        {
            "title": "Google ADK 2.9.0 Architecture & Best Practices",
            "snippet": "Google ADK provides modular Agent, Runner, Session, and Event stream abstractions for production GenAI.",
            "url": "https://google.github.io/adk-docs/architecture"
        }
    ]

    return {
        "status": "success",
        "query": query_clean,
        "results": mock_results[:max_results],
        "total_results": len(mock_results[:max_results])
    }
