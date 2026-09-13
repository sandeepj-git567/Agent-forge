"""
Vector Storage and Similarity Search Engine for AgentForge AI
"""
from typing import Any

import numpy as np
from pydantic import BaseModel, Field

from agentforge.rag.chunker import TextChunk
from agentforge.rag.embeddings import EmbeddingEngine, default_embedding_engine


class SearchResult(BaseModel):
    """Vector search result container with relevance metrics and metadata."""
    chunk_id: str
    doc_id: str
    filename: str
    content: str
    similarity_score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class VectorStore:
    """In-Memory and SQL Vector Storage Engine with Cosine Similarity Search."""

    def __init__(self, embedding_engine: EmbeddingEngine | None = None) -> None:
        self.embedding_engine = embedding_engine or default_embedding_engine
        self._chunks: dict[str, dict[str, Any]] = {}

    def add_document(self, doc_id: str, filename: str, chunks: list[TextChunk]) -> int:
        """Embed and store document chunks."""
        if not chunks:
            return 0

        texts = [c.content for c in chunks]
        embeddings = self.embedding_engine.embed_batch(texts)

        for chunk, vec in zip(chunks, embeddings):
            chunk_key = f"{doc_id}_{chunk.chunk_index}"
            self._chunks[chunk_key] = {
                "chunk_id": chunk_key,
                "doc_id": doc_id,
                "filename": filename,
                "content": chunk.content,
                "embedding": np.array(vec, dtype=np.float32),
                "metadata": chunk.metadata
            }

        return len(chunks)

    def similarity_search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.3,
        metadata_filter: dict[str, Any] | None = None
    ) -> list[SearchResult]:
        """Perform vector cosine similarity search over stored document chunks."""
        if not self._chunks or not query or not query.strip():
            return []

        query_vec = np.array(self.embedding_engine.embed_text(query), dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)

        if query_norm == 0:
            return []

        results: list[SearchResult] = []

        for item in self._chunks.values():
            # Apply metadata filtering if specified
            if metadata_filter:
                match = True
                for k, v in metadata_filter.items():
                    if item["metadata"].get(k) != v and item.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            doc_vec = item["embedding"]
            doc_norm = np.linalg.norm(doc_vec)

            if doc_norm == 0:
                continue

            similarity = float(np.dot(query_vec, doc_vec) / (query_norm * doc_norm))

            if similarity >= min_similarity:
                results.append(
                    SearchResult(
                        chunk_id=item["chunk_id"],
                        doc_id=item["doc_id"],
                        filename=item["filename"],
                        content=item["content"],
                        similarity_score=round(similarity, 4),
                        metadata=item["metadata"]
                    )
                )

        # Sort descending by similarity score
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]

    def clear(self) -> None:
        """Clear vector store contents."""
        self._chunks.clear()


default_vector_store = VectorStore()
