"""
Vector RAG Search and Q&A API Router (RagSys Enhanced)
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


class RAGQuestionRequest(BaseModel):
    """Payload for POST /api/v1/rag/ask"""
    question: str = Field(..., description="User question string", json_schema_extra={"example": "Summarize the architecture of AgentForge AI"})
    top_k: int = Field(default=5, description="Number of context chunks to retrieve")


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


@router.post("/ask")
async def rag_ask_question(payload: RAGQuestionRequest) -> dict[str, Any]:
    """
    RagSys-style Q&A Endpoint: Answer questions over ingested PDF/MD document knowledge base.
    """
    response = default_rag_engine.query_rag(
        query=payload.question,
        top_k=payload.top_k
    )
    return {
        "status": "success" if response.is_sufficient_evidence else "insufficient_evidence",
        "question": payload.question,
        "answer": response.answer,
        "confidence_score": response.confidence_score,
        "citations": response.citations,
        "chunks_used": len(response.citations)
    }
