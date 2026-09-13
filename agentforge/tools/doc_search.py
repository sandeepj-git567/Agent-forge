"""
Document Search Interface Tool for AgentForge AI (Phase 2 RAG Powered)
"""
from typing import Any

from agentforge.rag.rag_engine import default_rag_engine


def document_search(query: str, category: str = "all") -> dict[str, Any]:
    """
    Interface for searching internal documents via Vector RAG Engine (READ_ONLY category).
    """
    query_clean = query.strip()
    if not query_clean:
        return {"status": "error", "message": "Document search query cannot be empty", "documents": []}

    rag_response = default_rag_engine.query_rag(query=query_clean)

    documents_found: list[dict[str, Any]] = [
        {
            "chunk_id": chunk.chunk_id,
            "doc_id": chunk.doc_id,
            "filename": chunk.filename,
            "content": chunk.content,
            "similarity_score": chunk.similarity_score
        }
        for chunk in rag_response.retrieved_chunks
    ]

    return {
        "status": "success" if rag_response.is_sufficient_evidence else "insufficient_evidence",
        "query": query_clean,
        "category": category,
        "confidence_score": rag_response.confidence_score,
        "answer_summary": rag_response.answer,
        "citations": rag_response.citations,
        "documents": documents_found,
        "count": len(documents_found)
    }
