"""Vector store client supporting Qdrant with in-memory cosine fallback."""

import logging
import uuid
from typing import Any, Dict, List, Optional
from app.config import get_settings

logger = logging.getLogger("software-blueprint-ai.qdrant")

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
except ImportError:
    QdrantClient = None
    PointStruct = None


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorStoreManager:
    """Vector database manager with Qdrant and in-memory cosine similarity fallback."""

    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[Any] = None
        self._memory_points: List[Dict[str, Any]] = []
        self._is_qdrant_available = False
        self._init_qdrant()

    def _init_qdrant(self):
        if QdrantClient is None:
            logger.info("qdrant-client not installed. Using in-memory vector store.")
            return

        try:
            client = QdrantClient(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key or None,
                timeout=1.0
            )
            # Ping collections
            client.get_collections()
            self.client = client
            self._is_qdrant_available = True
            logger.info("Connected to Qdrant at %s", self.settings.qdrant_url)
            self._ensure_collection()
        except Exception as e:
            logger.info("Qdrant unreachable (%s). Using high-performance in-memory vector store.", e)
            self._is_qdrant_available = False

    def _ensure_collection(self, dim: int = 384):
        if not self._is_qdrant_available or not self.client:
            return
        try:
            colls = [c.name for c in self.client.get_collections().collections]
            if self.settings.qdrant_collection_name not in colls:
                self.client.create_collection(
                    collection_name=self.settings.qdrant_collection_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
                )
                logger.info("Created Qdrant collection: %s", self.settings.qdrant_collection_name)
        except Exception as e:
            logger.warning("Could not ensure Qdrant collection: %s", e)

    def upsert_points(self, points: List[Dict[str, Any]]) -> bool:
        """Upsert document vector points with payload metadata."""
        # Always update memory store
        for p in points:
            # Replace existing point if same id
            self._memory_points = [x for x in self._memory_points if x["id"] != p["id"]]
            self._memory_points.append(p)

        # Upsert into Qdrant if available
        if self._is_qdrant_available and self.client:
            try:
                q_points = [
                    PointStruct(
                        id=str(uuid.uuid5(uuid.NAMESPACE_DNS, str(p["id"]))),
                        vector=p["vector"],
                        payload=p["payload"]
                    )
                    for p in points
                ]
                self.client.upsert(
                    collection_name=self.settings.qdrant_collection_name,
                    points=q_points
                )
                return True
            except Exception as e:
                logger.warning("Failed to upsert points to Qdrant: %s", e)
        return True

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search top-k most relevant chunks using vector similarity."""
        # 1. Try Qdrant if available
        if self._is_qdrant_available and self.client:
            try:
                results = self.client.search(
                    collection_name=self.settings.qdrant_collection_name,
                    query_vector=query_vector,
                    limit=top_k
                )
                if results:
                    return [
                        {
                            "id": str(r.id),
                            "score": float(r.score),
                            "payload": r.payload
                        }
                        for r in results
                    ]
            except Exception as e:
                logger.warning("Qdrant search error (%s). Falling back to memory search.", e)

        # 2. In-memory cosine search fallback
        scored = []
        for p in self._memory_points:
            score = cosine_similarity(query_vector, p["vector"])
            scored.append({
                "id": str(p["id"]),
                "score": float(score),
                "payload": p["payload"]
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def count(self) -> int:
        return len(self._memory_points)

    def get_status(self) -> Dict[str, Any]:
        """Return connectivity and collection status for Qdrant and memory store."""
        status_info = {
            "qdrant_available": self._is_qdrant_available,
            "qdrant_url": self.settings.qdrant_url,
            "dashboard_url": f"{self.settings.qdrant_url.rstrip('/')}/dashboard",
            "collection_name": self.settings.qdrant_collection_name,
            "vector_dimension": 384,
            "distance_metric": "Cosine",
            "total_indexed_chunks": len(self._memory_points),
            "backend": "Qdrant Vector Engine" if self._is_qdrant_available else "In-Memory Vector Engine (Offline Fallback)",
            "how_to_view": (
                "Open http://localhost:6333/dashboard in your web browser. "
                "Navigate to 'Collections' -> 'software_architecture_knowledge'. "
                "You can visually inspect points, dense vectors (384-dim), and JSON payloads."
            )
        }
        return status_info


# Global singleton instance
vector_store = VectorStoreManager()
