"""
Document Management and Upload API Router
"""
import uuid
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from agentforge.guardrails.input_guard import default_input_guard
from agentforge.rag.chunker import default_chunker
from agentforge.rag.extractor import default_extractor
from agentforge.rag.store import default_vector_store

router = APIRouter(prefix="/documents", tags=["Document Management"])

# In-memory document metadata store (Phase 2 API layer)
_DOCUMENT_STORE: dict[str, dict[str, Any]] = {}


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)) -> dict[str, Any]:  # noqa: B008
    """
    Upload, extract, chunk, embed, and store document in vector search index.
    Supports PDF, DOCX, TXT, MD.
    """
    filename = file.filename or "uploaded_document.txt"
    content_bytes = await file.read()

    # Guardrail Validation
    is_valid, err_msg = default_input_guard.validate_file_upload(filename, len(content_bytes))
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

    try:
        # Extract text
        extracted_text, meta = default_extractor.extract_text(content_bytes, filename)
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    except Exception as err:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Text extraction failed: {err!s}")

    # Chunk text
    chunks = default_chunker.chunk_document(extracted_text, meta)

    # Embed and store in vector search store
    doc_id = f"doc-{uuid.uuid4().hex[:8]}"
    chunks_stored = default_vector_store.add_document(doc_id=doc_id, filename=filename, chunks=chunks)

    doc_meta = {
        "doc_id": doc_id,
        "filename": filename,
        "file_size": len(content_bytes),
        "num_chunks": chunks_stored,
        "status": "processed",
        "metadata": meta
    }
    _DOCUMENT_STORE[doc_id] = doc_meta

    return {
        "status": "success",
        "message": f"Document '{filename}' ingested successfully.",
        "document": doc_meta
    }


@router.get("", response_model=list[dict[str, Any]])
async def list_documents() -> list[dict[str, Any]]:
    """List all uploaded documents."""
    return list(_DOCUMENT_STORE.values())


@router.delete("/{doc_id}")
async def delete_document(doc_id: str) -> dict[str, Any]:
    """Remove document from repository."""
    if doc_id not in _DOCUMENT_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document ID '{doc_id}' not found.")

    doc = _DOCUMENT_STORE.pop(doc_id)
    return {"status": "success", "message": f"Document '{doc['filename']}' deleted successfully."}
