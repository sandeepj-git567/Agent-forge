"""
Vector RAG Search and Q&A API Router (RagSys Enhanced)
"""
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from agentforge.config.settings import settings
from agentforge.rag.rag_engine import default_rag_engine

router = APIRouter(prefix="/rag", tags=["Vector RAG Search"])


class RAGSearchRequest(BaseModel):
    """Payload for POST /api/v1/rag/search"""
    query: str = Field(..., description="User query string", json_schema_extra={"example": "What is AgentForge AI?"})
    top_k: int = Field(default=5, description="Number of vector results to retrieve")
    metadata_filter: dict[str, Any] | None = Field(default=None, description="Optional metadata filter rules")


class RAGQuestionRequest(BaseModel):
    """Payload for POST /api/v1/rag/ask or POST /api/v1/rag/answer"""
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

    fallback_used = not settings.is_gemini_configured

    return {
        "query": payload.query,
        "results_count": len(response.citations),
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "fallback_used": fallback_used,
        "results": response.citations
    }


@router.post("/answer")
@router.post("/ask")
async def rag_answer_question(payload: RAGQuestionRequest) -> dict[str, Any]:
    """
    RAG Q&A Endpoint: Answer questions over ingested PDF/MD document knowledge base.
    Returns structured answer, source citations, embedding provider, retrieval count, and fallback status.
    """
    response = default_rag_engine.query_rag(
        query=payload.question,
        top_k=payload.top_k
    )

    fallback_used = not settings.is_gemini_configured

    sources = [
        {
            "document_id": getattr(c, "doc_id", c.get("doc_id", "N/A")),
            "filename": getattr(c, "source_doc", c.get("source_doc", "document")),
            "chunk_id": getattr(c, "chunk_id", c.get("chunk_id", "N/A")),
            "page": getattr(c, "page", c.get("page", 1)),
            "similarity_score": getattr(c, "similarity_score", c.get("similarity_score", 0.0)),
            "content": getattr(c, "text_snippet", c.get("text_snippet", ""))
        }
        for c in response.citations
    ]

    return {
        "status": "success" if response.is_sufficient_evidence else "insufficient_evidence",
        "question": payload.question,
        "answer": response.answer,
        "sources": sources,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "retrieval_count": len(sources),
        "fallback_used": fallback_used,
        "confidence_score": response.confidence_score,
        "citations": response.citations,
        "chunks_used": len(sources)
    }

