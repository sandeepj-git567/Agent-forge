"""
Recursive Text Chunking Algorithm for AgentForge AI RAG Pipeline
"""
import hashlib
from typing import Any

from pydantic import BaseModel, Field


class TextChunk(BaseModel):
    """Container for a single text chunk with metadata."""
    chunk_index: int
    content: str
    chunk_hash: str
    token_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentChunker:
    """Splits documents into overlapping chunks with position tracking."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, text: str, source_metadata: dict[str, Any]) -> list[TextChunk]:
        """Split text string into TextChunk objects."""
        if not text or not text.strip():
            return []

        chunks: list[TextChunk] = []
        text_clean = text.strip()
        length = len(text_clean)
        start = 0
        chunk_idx = 0

        while start < length:
            end = start + self.chunk_size

            # If not at the end of text, try breaking on whitespace/paragraph break
            if end < length:
                last_space = text_clean.rfind(" ", start, end)
                if last_space != -1 and last_space > start + (self.chunk_size // 2):
                    end = last_space

            chunk_text = text_clean[start:end].strip()

            if chunk_text:
                chunk_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()[:16]
                token_count = len(chunk_text.split())

                chunk_meta = {
                    **source_metadata,
                    "start_char": start,
                    "end_char": end,
                    "chunk_size": len(chunk_text)
                }

                chunks.append(
                    TextChunk(
                        chunk_index=chunk_idx,
                        content=chunk_text,
                        chunk_hash=chunk_hash,
                        token_count=token_count,
                        metadata=chunk_meta
                    )
                )
                chunk_idx += 1

            start = end - self.chunk_overlap if end < length else length

        return chunks


default_chunker = DocumentChunker()
