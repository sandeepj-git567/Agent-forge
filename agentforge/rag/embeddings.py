"""
Embedding Generation Engine for AgentForge AI RAG

Supports both Google Gemini Embeddings (text-embedding-004) and local SentenceTransformers.
"""
import numpy as np
from google.genai import client as genai_client
from sentence_transformers import SentenceTransformer

from agentforge.config.settings import settings


class EmbeddingEngine:
    """Unified Embedding Engine with Gemini Embeddings and SentenceTransformers fallback."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> list[float]:
        """Generate normalized embedding vector for a single string."""
        if not text or not text.strip():
            return [0.0] * 384

        if settings.is_api_key_configured:
            try:
                ai_client = genai_client.Client(api_key=settings.GOOGLE_API_KEY)
                response = ai_client.models.embed_content(
                    model="text-embedding-004",
                    contents=text
                )
                if response.embedding and response.embedding.values:
                    vec = np.array(response.embedding.values, dtype=np.float32)
                    norm = np.linalg.norm(vec)
                    if norm > 0:
                        vec = vec / norm
                    return vec.tolist()
            except Exception:  # noqa: BLE001, S110
                # Fallback to SentenceTransformer when Gemini API call fails or is un-configured
                pass

        model = self._get_model()
        vec = model.encode(text, normalize_embeddings=True)
        return vec.tolist() if isinstance(vec, np.ndarray) else list(vec)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate normalized embedding vectors for a batch of strings."""
        if not texts:
            return []

        return [self.embed_text(t) for t in texts]


default_embedding_engine = EmbeddingEngine()
