"""Tests for Module 4: RAG System, Vector Store, and Grounded Retrieval."""

import pytest
from app.rag.embeddings import get_embedding
from app.rag.qdrant_client import vector_store, cosine_similarity
from app.rag.retriever import retrieve_relevant_evidence, load_and_ingest_knowledge_base
from app.schemas import RAGEvidence


def test_embedding_generation_and_caching():
    text = "Clean architecture and dependency inversion in Python"
    vec1 = get_embedding(text)
    vec2 = get_embedding(text)
    assert len(vec1) > 0
    assert vec1 == vec2  # Cached vector equality


def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    assert pytest.approx(cosine_similarity(v1, v2), 0.001) == 1.0
    assert pytest.approx(cosine_similarity(v1, v3), 0.001) == 0.0


def test_knowledge_base_ingestion_and_retrieval():
    total_indexed = load_and_ingest_knowledge_base()
    assert total_indexed > 0

    evidence = retrieve_relevant_evidence("Event-driven messaging and microservices", top_k=2)
    assert len(evidence) <= 2
    assert len(evidence) > 0
    assert isinstance(evidence[0], RAGEvidence)
    assert evidence[0].source_id != ""
    assert evidence[0].title != ""
    assert evidence[0].relevance_score > 0.0
