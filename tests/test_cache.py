"""Tests for Caching and Embedding Memory / Redis layer."""

import pytest
from app.cache.redis_client import cache_manager
from app.llm.factory import MetricsTracker


def test_cache_set_and_get():
    key = "test:operation:123"
    value = {"status": "success", "data": [1, 2, 3]}
    
    cache_manager.set(key, value, ttl=60)
    retrieved = cache_manager.get(key)
    
    assert retrieved == value


def test_embedding_cache():
    text = "Query text for vector cache test"
    vector = [0.1, 0.2, 0.3, 0.4]
    
    cache_manager.set_embedding(text, vector, model="test-embed")
    retrieved = cache_manager.get_embedding(text, model="test-embed")
    
    assert retrieved == vector


def test_selective_invalidation():
    k1 = "arch:FR-001:v1"
    k2 = "arch:FR-002:v1"
    cache_manager.set(k1, {"data": "fr1"})
    cache_manager.set(k2, {"data": "fr2"})
    
    cache_manager.invalidate_by_dependency("FR-001")
    
    assert cache_manager.get(k1) is None
    assert cache_manager.get(k2) is not None


def test_metrics_tracker():
    MetricsTracker.reset()
    MetricsTracker.record_llm_call(150.0, input_chars=400, output_chars=200)
    MetricsTracker.record_cache_hit(saved_chars=1000)
    
    summary = MetricsTracker.get_summary()
    assert summary["total_llm_calls"] == 1
    assert summary["cache_hits"] == 1
    assert summary["estimated_input_tokens"] > 0
