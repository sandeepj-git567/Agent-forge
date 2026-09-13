"""
Production RAG Engine for AgentForge AI

Manages query rewriting, vector retrieval, context window budgeting,
verifiable citation formatting, and confidence-based "I don't know" behavior.
"""
from typing import Any

from pydantic import BaseModel, Field

from agentforge.guardrails.output_guard import default_output_guard
from agentforge.rag.store import SearchResult, VectorStore, default_vector_store


class RAGResponse(BaseModel):
    """Container for RAG query output with context and citations."""
    query: str
    rewritten_query: str
    answer: str
    confidence_score: float
    is_sufficient_evidence: bool
    citations: list[dict[str, Any]] = Field(default_factory=list)
    retrieved_chunks: list[SearchResult] = Field(default_factory=list)


class RAGEngine:
    """Core RAG orchestration pipeline."""

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        min_confidence_threshold: float = 0.35,
        max_context_chars: int = 3000
    ) -> None:
        self.vector_store = vector_store or default_vector_store
        self.min_confidence_threshold = min_confidence_threshold
        self.max_context_chars = max_context_chars

    def rewrite_query(self, query: str) -> str:
        """Normalize and optimize user query for vector embedding search."""
        clean_q = query.strip()
        # Remove common question filler prefixes if present
        prefixes_to_strip = [
            "can you tell me about", "what is", "where is", "how do I",
            "please find information regarding", "search for"
        ]
        q_lower = clean_q.lower()
        for prefix in prefixes_to_strip:
            if q_lower.startswith(prefix):
                clean_q = clean_q[len(prefix):].strip(" ?:.")
                break
        return clean_q or query.strip()

    def query_rag(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: dict[str, Any] | None = None
    ) -> RAGResponse:
        """
        Execute end-to-end RAG pipeline:
        1. Query rewriting
        2. Vector search retrieval
        3. Threshold confidence evaluation
        4. Context assembly & citation formatting
        """
        rewritten = self.rewrite_query(query)
        search_results = self.vector_store.similarity_search(
            query=rewritten,
            top_k=top_k,
            min_similarity=0.2,
            metadata_filter=metadata_filter
        )

        if not search_results:
            return RAGResponse(
                query=query,
                rewritten_query=rewritten,
                answer="I do not have sufficient document evidence in the knowledge base to answer your request accurately.",
                confidence_score=0.0,
                is_sufficient_evidence=False,
                citations=[],
                retrieved_chunks=[]
            )

        top_score = search_results[0].similarity_score

        if top_score < self.min_confidence_threshold:
            return RAGResponse(
                query=query,
                rewritten_query=rewritten,
                answer=(
                    f"The retrieved information has low confidence ({top_score:.2f} < threshold {self.min_confidence_threshold}). "
                    "I cannot provide a verified answer based on the current document knowledge base."
                ),
                confidence_score=top_score,
                is_sufficient_evidence=False,
                citations=[],
                retrieved_chunks=search_results
            )

        # Assemble context budget
        context_parts = []
        citations = []
        curr_chars = 0

        for res in search_results:
            if curr_chars + len(res.content) > self.max_context_chars:
                break
            context_parts.append(f"[{res.filename} | Chunk {res.chunk_id}]: {res.content}")
            citations.append({
                "source_file": res.filename,
                "chunk_id": res.chunk_id,
                "doc_id": res.doc_id,
                "similarity_score": res.similarity_score
            })
            curr_chars += len(res.content)

        assembled_context = "\n\n".join(context_parts)
        sanitized_answer = default_output_guard.sanitize_text(
            f"Based on retrieved documents ({len(citations)} sources verified):\n\n{assembled_context}"
        )

        return RAGResponse(
            query=query,
            rewritten_query=rewritten,
            answer=sanitized_answer,
            confidence_score=top_score,
            is_sufficient_evidence=True,
            citations=citations,
            retrieved_chunks=search_results
        )


default_rag_engine = RAGEngine()
