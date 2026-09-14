"""
Comprehensive Tests for Phase 2 RAG Pipeline, Database Models, and Document Upload API
"""
import io

import pytest
from fastapi.testclient import TestClient

from agentforge.api.main import app
from agentforge.db.models import Document, DocumentChunk, Embedding, User
from agentforge.rag.chunker import default_chunker
from agentforge.rag.embeddings import default_embedding_engine
from agentforge.rag.extractor import default_extractor
from agentforge.rag.rag_engine import RAGEngine
from agentforge.rag.store import VectorStore

client = TestClient(app)


def test_db_models_instantiation():
    user = User(email="test@agentforge.ai", hashed_password="hashed_secret_pw")
    doc = Document(filename="architecture.pdf", file_type="pdf", file_size=1024, content_hash="hash123")
    chunk = DocumentChunk(document_id=doc.id, chunk_index=0, content="AgentForge AI Architecture")
    emb = Embedding(chunk_id=chunk.id, embedding_model="all-MiniLM-L6-v2", vector_data=[0.1] * 384)

    assert user.email == "test@agentforge.ai"
    assert doc.filename == "architecture.pdf"
    assert chunk.content == "AgentForge AI Architecture"
    assert len(emb.vector_data) == 384


def test_text_extractor_unsupported_file():
    with pytest.raises(ValueError, match="Unsupported file format"):
        default_extractor.extract_text(b"some content", "file.exe")


def test_document_chunker():
    text = "Word " * 200
    chunks = default_chunker.chunk_document(text, {"filename": "test.txt"})
    assert len(chunks) > 0
    assert chunks[0].token_count > 0
    assert chunks[0].chunk_hash is not None


def test_embedding_engine():
    vec = default_embedding_engine.embed_text("Enterprise AI Agent Framework")
    assert isinstance(vec, list)
    assert len(vec) == 384


def test_vector_store_and_rag_engine():
    store = VectorStore()
    text = "AgentForge AI uses Google ADK 2.9.0 and pgvector for enterprise multi-agent workflows."
    chunks = default_chunker.chunk_document(text, {"filename": "blueprint.txt"})
    store.add_document("doc-100", "blueprint.txt", chunks)

    rag = RAGEngine(vector_store=store, min_confidence_threshold=0.2)

    # Relevant query test
    res = rag.query_rag("What framework does AgentForge AI use?")
    assert res.is_sufficient_evidence is True
    assert len(res.citations) > 0
    assert "Google ADK 2.9.0" in res.answer

    # Irrelevant query test (insufficient evidence)
    res_irrelevant = rag.query_rag("How do I fix a broken car engine component?")
    assert res_irrelevant.is_sufficient_evidence is False
    assert any(term in res_irrelevant.answer.lower() for term in ["low confidence", "insufficient", "do not have"])


def test_document_upload_api():
    file_content = b"# AgentForge System Spec\nAgentForge AI supports multi-agent orchestration and pgvector RAG."
    files = {"file": ("spec.md", io.BytesIO(file_content), "text/markdown")}

    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "doc_id" in data["document"]
    assert data["document"]["num_chunks"] > 0


def test_document_upload_path_traversal_blocked():
    file_content = b"Malicious content"
    files = {"file": ("../../etc/passwd", io.BytesIO(file_content), "text/plain")}

    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 400
    assert "path traversal" in response.json()["detail"].lower()


def test_rag_search_api():
    req_body = {
        "query": "AgentForge AI spec",
        "top_k": 3
    }
    response = client.post("/api/v1/rag/search", json=req_body)
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "embedding_provider" in data
    assert "fallback_used" in data


def test_rag_ask_api():
    req_body = {
        "question": "What is AgentForge AI?",
        "top_k": 3
    }
    response = client.post("/api/v1/rag/ask", json=req_body)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "confidence_score" in data
    assert "citations" in data


def test_rag_answer_api():
    req_body = {
        "question": "What is AgentForge AI?",
        "top_k": 3
    }
    response = client.post("/api/v1/rag/answer", json=req_body)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "embedding_provider" in data
    assert "retrieval_count" in data
    assert "fallback_used" in data


def test_document_upload_executable_blocked():
    file_content = b"echo 'hacked'"
    files = {"file": ("malicious_script.sh", io.BytesIO(file_content), "application/x-sh")}

    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 400
    assert "prohibited" in response.json()["detail"].lower() or "unsupported" in response.json()["detail"].lower()


def test_document_get_and_delete_api():
    file_content = b"Unique document content for lifecycle testing."
    files = {"file": ("lifecycle.txt", io.BytesIO(file_content), "text/plain")}

    # 1. Upload
    up_res = client.post("/api/v1/documents/upload", files=files)
    assert up_res.status_code == 201
    doc_id = up_res.json()["document"]["doc_id"]

    # 2. Get document inspect
    get_res = client.get(f"/api/v1/documents/{doc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["doc_id"] == doc_id
    assert get_res.json()["filename"] == "lifecycle.txt"

    # 3. Delete document
    del_res = client.delete(f"/api/v1/documents/{doc_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # 4. Verify 404 after deletion
    get_after = client.get(f"/api/v1/documents/{doc_id}")
    assert get_after.status_code == 404

