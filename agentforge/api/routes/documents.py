"""
Document Management and Upload API Router
"""
import hashlib
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from agentforge.config.settings import settings
from agentforge.db.repositories.document_repository import DocumentRepository
from agentforge.db.session import get_db
from agentforge.guardrails.input_guard import default_input_guard
from agentforge.rag.chunker import default_chunker
from agentforge.rag.extractor import default_extractor
from agentforge.rag.store import default_vector_store

router = APIRouter(prefix="/documents", tags=["Document Management"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),  # noqa: B008
    db: Session = Depends(get_db)
) -> dict[str, Any]:
    """
    Upload, validate, calculate SHA-256 hash, extract, chunk, embed, and persist document.
    Supports PDF, DOCX, TXT, MD. Prevents duplicate uploads using SHA-256.
    """
    filename = file.filename or "uploaded_document.txt"
    content_bytes = await file.read()

    # File & Path Traversal Guardrail Validation
    is_valid, err_msg = default_input_guard.validate_file_upload(filename, len(content_bytes))
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

    # SHA-256 Hash Generation
    content_hash = hashlib.sha256(content_bytes).hexdigest()

    # Database repository check for duplicate uploads
    doc_repo = DocumentRepository(db)
    existing_doc = doc_repo.get_by_content_hash(content_hash)
    if existing_doc:
        return {
            "status": "duplicate_detected",
            "message": f"Document '{filename}' with identical hash has already been ingested.",
            "document": {
                "doc_id": existing_doc.id,
                "filename": existing_doc.filename,
                "file_size": existing_doc.file_size,
                "content_hash": existing_doc.content_hash,
                "num_chunks": len(existing_doc.chunks),
                "status": existing_doc.status,
                "created_at": existing_doc.created_at.isoformat() if existing_doc.created_at else None
            }
        }

    try:
        # Text extraction
        extracted_text, meta = default_extractor.extract_text(content_bytes, filename)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as err:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Text extraction failed: {err!s}")

    # Recursive chunking
    chunks = default_chunker.chunk_document(extracted_text, meta)

    # Vector store indexing
    doc_id = f"doc-{uuid.uuid4().hex[:8]}"
    chunks_stored = default_vector_store.add_document(doc_id=doc_id, filename=filename, chunks=chunks)

    # Persist in Database Repository
    db_doc = doc_repo.create_document(
        filename=filename,
        file_type=file.content_type or "application/octet-stream",
        file_size=len(content_bytes),
        content_hash=content_hash,
        meta_info={
            "embedding_provider": settings.EMBEDDING_PROVIDER,
            "embedding_model": "text-embedding-004",
            "chunk_count": chunks_stored,
            "char_count": len(extracted_text)
        }
    )

    chunks_payload = [
        {
            "chunk_index": c.chunk_index,
            "content": c.content,
            "token_count": len(c.content.split()),
            "metadata": c.metadata,
            "embedding_model": "text-embedding-004"
        }
        for c in chunks
    ]
    doc_repo.add_chunks(document_id=db_doc.id, chunks_data=chunks_payload)

    doc_meta = {
        "doc_id": db_doc.id,
        "filename": filename,
        "content_type": file.content_type or "text/plain",
        "file_size": len(content_bytes),
        "content_hash": content_hash,
        "num_chunks": chunks_stored,
        "status": "processed",
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "embedding_model": "text-embedding-004",
        "metadata": meta
    }

    return {
        "status": "success",
        "message": f"Document '{filename}' ingested successfully into vector database.",
        "document": doc_meta
    }


@router.get("", response_model=list[dict[str, Any]])
async def list_documents(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """List all uploaded documents from database."""
    doc_repo = DocumentRepository(db)
    docs = doc_repo.list_documents()

    return [
        {
            "doc_id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "content_hash": doc.content_hash,
            "num_chunks": len(doc.chunks),
            "status": doc.status,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "meta_info": doc.meta_info
        }
        for doc in docs
    ]


@router.get("/{document_id}")
async def get_document(document_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Retrieve detailed document metadata and chunk stats."""
    doc_repo = DocumentRepository(db)
    doc = doc_repo.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document ID '{document_id}' not found.")

    return {
        "doc_id": doc.id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "file_size": doc.file_size,
        "content_hash": doc.content_hash,
        "num_chunks": len(doc.chunks),
        "status": doc.status,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "meta_info": doc.meta_info,
        "chunks_preview": [
            {
                "chunk_id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "token_count": chunk.token_count,
                "snippet": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
            }
            for chunk in doc.chunks[:5]
        ]
    }


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Delete document and cascade delete all associated chunks and embeddings."""
    doc_repo = DocumentRepository(db)
    success = doc_repo.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document ID '{document_id}' not found.")

    return {"status": "success", "message": f"Document '{document_id}' and associated chunks deleted successfully."}

