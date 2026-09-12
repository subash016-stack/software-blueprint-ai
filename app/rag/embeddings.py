"""Embedding generator with SHA-256 caching and Ollama / local vectorizer support."""

import hashlib
import logging
from typing import List, Optional
import httpx

from app.config import get_settings
from app.cache.redis_client import cache_manager

logger = logging.getLogger("software-blueprint-ai.embeddings")


def _generate_synthetic_dense_vector(text: str, dim: int = 384) -> List[float]:
    """Deterministic hash-based dense vector for offline/zero-dependency environments."""
    # Deterministic pseudo-random seed from MD5 hash
    h = hashlib.sha256(text.encode("utf-8")).digest()
    vector = []
    for i in range(dim):
        byte_idx = i % len(h)
        val = ((h[byte_idx] + i * 37) % 256) / 255.0 - 0.5
        vector.append(float(val))
    # Normalize vector to unit length
    magnitude = sum(x * x for x in vector) ** 0.5
    return [round(x / max(magnitude, 1e-9), 6) for x in vector]


_ollama_embeddings_failed = False


def get_embedding(text: str, model_override: Optional[str] = None) -> List[float]:
    """Compute dense embedding vector with SHA-256 caching."""
    global _ollama_embeddings_failed
    if not text or not text.strip():
        return [0.0] * 384

    settings = get_settings()
    model = model_override or settings.embedding_model

    # 1. Check cache
    cached_vec = cache_manager.get_embedding(text, model)
    if cached_vec:
        return cached_vec

    # 2. Try Ollama Embeddings API (if not marked unavailable)
    if not _ollama_embeddings_failed:
        try:
            url = f"{settings.ollama_base_url}/api/embeddings"
            payload = {"model": model, "prompt": text.strip()}
            with httpx.Client(timeout=5.0) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 200:
                    vector = resp.json().get("embedding", [])
                    if vector and len(vector) > 0:
                        cache_manager.set_embedding(text, vector, model)
                        return vector
        except Exception:
            _ollama_embeddings_failed = True

    # 3. Fallback deterministic dense vector
    vector = _generate_synthetic_dense_vector(text)
    cache_manager.set_embedding(text, vector, model)
    return vector
