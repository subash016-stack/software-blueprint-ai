"""Redis cache with resilient in-memory fallback and dependency-aware invalidation."""

import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional
from app.config import get_settings
from app.llm.factory import MetricsTracker

logger = logging.getLogger("software-blueprint-ai.cache")

try:
    import redis
except ImportError:
    redis = None


class CacheManager:
    """Manages Redis cache with automatic in-memory fallback for offline/local execution."""

    def __init__(self):
        self.settings = get_settings()
        self._redis_client: Optional[Any] = None
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._embedding_cache: Dict[str, List[float]] = {}
        self._is_redis_available = False
        self._init_redis()

    def _init_redis(self):
        if not self.settings.enable_redis or redis is None:
            logger.info("Redis disabled or package not available. Using high-performance in-memory cache.")
            return

        try:
            client = redis.Redis.from_url(
                self.settings.redis_url,
                socket_timeout=1.0,
                socket_connect_timeout=1.0,
                decode_responses=True
            )
            client.ping()
            self._redis_client = client
            self._is_redis_available = True
            logger.info("Connected to Redis cache at %s", self.settings.redis_url)
        except Exception as e:
            logger.info("Redis unreachable (%s). Using fallback in-memory cache.", e)
            self._is_redis_available = False

    def build_cache_key(
        self,
        operation: str,
        input_data: Any,
        prompt_version: str = "1.0",
        schema_version: str = "1.0",
        model: Optional[str] = None
    ) -> str:
        """Build deterministic cache key: operation:input_hash:model:prompt_ver:schema_ver."""
        model_name = model or self.settings.generation_model
        if isinstance(input_data, str):
            content_bytes = input_data.encode("utf-8")
        elif isinstance(input_data, dict) or isinstance(input_data, list):
            content_bytes = json.dumps(input_data, sort_keys=True).encode("utf-8")
        else:
            content_bytes = str(input_data).encode("utf-8")

        input_hash = hashlib.sha256(content_bytes).hexdigest()[:16]
        return f"{operation}:{input_hash}:{model_name}:p{prompt_version}:s{schema_version}"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached JSON dict if present and not expired."""
        # 1. Try Redis
        if self._is_redis_available and self._redis_client:
            try:
                data_str = self._redis_client.get(key)
                if data_str:
                    MetricsTracker.record_cache_hit(len(data_str))
                    return json.loads(data_str)
            except Exception as e:
                logger.warning("Redis GET error: %s", e)

        # 2. Try In-memory fallback
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if entry["expires_at"] > time.time():
                MetricsTracker.record_cache_hit(len(json.dumps(entry["value"])))
                return entry["value"]
            else:
                del self._memory_cache[key]

        MetricsTracker.record_cache_miss()
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in Redis and in-memory cache with TTL."""
        ttl_seconds = ttl or self.settings.cache_ttl_seconds
        payload_str = json.dumps(value, default=str)

        # 1. Store in Redis
        if self._is_redis_available and self._redis_client:
            try:
                self._redis_client.setex(key, ttl_seconds, payload_str)
            except Exception as e:
                logger.warning("Redis SET error: %s", e)

        # 2. Store in Memory
        self._memory_cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl_seconds
        }
        return True

    def get_embedding(self, text: str, model: Optional[str] = None) -> Optional[List[float]]:
        """Retrieve cached embedding vector by text + model hash."""
        target_model = model or self.settings.embedding_model
        key = f"embed:{hashlib.sha256((text + target_model).encode('utf-8')).hexdigest()}"

        if self._is_redis_available and self._redis_client:
            try:
                val = self._redis_client.get(key)
                if val:
                    MetricsTracker.record_cache_hit(len(val))
                    return json.loads(val)
            except Exception:
                pass

        if key in self._embedding_cache:
            MetricsTracker.record_cache_hit(200)
            return self._embedding_cache[key]

        return None

    def set_embedding(self, text: str, vector: List[float], model: Optional[str] = None) -> bool:
        """Cache embedding vector."""
        target_model = model or self.settings.embedding_model
        key = f"embed:{hashlib.sha256((text + target_model).encode('utf-8')).hexdigest()}"

        if self._is_redis_available and self._redis_client:
            try:
                self._redis_client.setex(key, self.settings.cache_ttl_seconds * 7, json.dumps(vector))
            except Exception:
                pass

        self._embedding_cache[key] = vector
        return True

    def invalidate_by_dependency(self, entity_id: str):
        """Selectively invalidate cache entries dependent on a specific entity ID."""
        logger.info("Invalidating cache dependencies for entity: %s", entity_id)
        # Scan in-memory cache
        keys_to_del = [k for k in self._memory_cache if entity_id in k]
        for k in keys_to_del:
            del self._memory_cache[k]

        # Scan Redis cache if connected
        if self._is_redis_available and self._redis_client:
            try:
                for match_key in self._redis_client.scan_iter(f"*{entity_id}*"):
                    self._redis_client.delete(match_key)
            except Exception as e:
                logger.warning("Redis invalidation error: %s", e)

    def clear(self):
        """Clear all cache entries."""
        self._memory_cache.clear()
        self._embedding_cache.clear()
        if self._is_redis_available and self._redis_client:
            try:
                self._redis_client.flushdb()
            except Exception:
                pass


# Global singleton instance
cache_manager = CacheManager()
