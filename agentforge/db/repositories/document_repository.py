"""
Document and Chunk Repository for Database Operations
"""
from typing import Sequence
from sqlalchemy.orm import Session
from agentforge.db.models import Document, DocumentChunk, Embedding


class DocumentRepository:
    """Repository handling CRUD operations for Document, DocumentChunk, and Embedding entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, doc_id: str, user_id: str | None = None) -> Document | None:
        """Fetch document by ID with optional ownership enforcement."""
        query = self.db.query(Document).filter(Document.id == doc_id)
        if user_id:
            query = query.filter(Document.user_id == user_id)
        return query.first()

    def get_by_content_hash(self, content_hash: str, user_id: str | None = None) -> Document | None:
        """Fetch document by SHA-256 content hash to prevent duplicate uploads."""
        query = self.db.query(Document).filter(Document.content_hash == content_hash)
        if user_id:
            query = query.filter(Document.user_id == user_id)
        return query.first()

    def create_document(
        self,
        filename: str,
        file_type: str,
        file_size: int,
        content_hash: str,
        user_id: str | None = None,
        meta_info: dict | None = None
    ) -> Document:
        """Create and persist a new Document metadata record."""
        doc = Document(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            content_hash=content_hash,
            meta_info=meta_info or {}
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def add_chunks(
        self,
        document_id: str,
        chunks_data: list[dict]
    ) -> list[DocumentChunk]:
        """Bulk create chunks and embeddings for a document."""
        chunks = []
        for cdata in chunks_data:
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=cdata["chunk_index"],
                content=cdata["content"],
                token_count=cdata.get("token_count", 0),
                chunk_metadata=cdata.get("metadata", {})
            )
            self.db.add(chunk)
            self.db.flush()

            if "embedding" in cdata:
                emb = Embedding(
                    chunk_id=chunk.id,
                    embedding_model=cdata.get("embedding_model", "text-embedding-004"),
                    vector_data=cdata["embedding"]
                )
                self.db.add(emb)

            chunks.append(chunk)

        self.db.commit()
        return chunks

    def list_documents(self, user_id: str | None = None, limit: int = 100) -> Sequence[Document]:
        """List documents with optional user filter."""
        query = self.db.query(Document)
        if user_id:
            query = query.filter(Document.user_id == user_id)
        return query.order_by(Document.created_at.desc()).limit(limit).all()

    def delete_document(self, doc_id: str, user_id: str | None = None) -> bool:
        """Delete document and cascade delete associated chunks & embeddings."""
        doc = self.get_by_id(doc_id, user_id=user_id)
        if not doc:
            return False
        self.db.delete(doc)
        self.db.commit()
        return True
