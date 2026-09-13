"""
Vector RAG Search API Router
"""
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from agentforge.rag.rag_engine import default_rag_engine

router = APIRouter(prefix="/rag", tags=["Vector RAG Search"])


class RAGSearchRequest(BaseModel):
    """Payload for POST /api/v1/rag/search"""
    query: str = Field(..., description="User query string", json_schema_extra={"example": "What is AgentForge AI?"})
    top_k: int = Field(default=5, description="Number of vector results to retrieve")
    metadata_filter: dict[str, Any] | None = Field(default=None, description="Optional metadata filter rules")


@router.post("/search")
async def rag_search(payload: RAGSearchRequest) -> dict[str, Any]:
    """
    Perform direct vector RAG similarity search and citation assembly.
    """
    response = default_rag_engine.query_rag(
        query=payload.query,
        top_k=payload.top_k,
        metadata_filter=payload.metadata_filter
    )
    return response.model_dump()
