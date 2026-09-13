"""
Embedding Generation Engine for AgentForge AI RAG
"""

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingEngine:
    """Generates vector embeddings for text chunks using SentenceTransformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self._model: SentenceTransformer | None = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> list[float]:
        """Generate normalized embedding vector for single string."""
        if not text or not text.strip():
            return [0.0] * 384

        model = self._get_model()
        vec = model.encode(text, normalize_embeddings=True)
        return vec.tolist() if isinstance(vec, np.ndarray) else list(vec)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate normalized embedding vectors for batch of strings."""
        if not texts:
            return []

        model = self._get_model()
        vecs = model.encode(texts, normalize_embeddings=True)
        return [v.tolist() if isinstance(v, np.ndarray) else list(v) for v in vecs]


default_embedding_engine = EmbeddingEngine()
