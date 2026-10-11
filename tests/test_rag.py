"""Tests for Module 4: RAG System, Vector Store, and Grounded Retrieval."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.rag.embeddings import get_embedding
from app.rag.qdrant_client import vector_store, cosine_similarity
from app.rag.retriever import (
    retrieve_relevant_evidence,
    load_and_ingest_knowledge_base,
    get_indexed_documents_catalog,
    get_all_indexed_chunks,
    parse_markdown_knowledge_file
)
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


def test_documents_catalog_and_hierarchical_chunking():
    catalog = get_indexed_documents_catalog()
    assert len(catalog) >= 7  # All 7 architecture docs cataloged

    doc_ids = {doc["document_id"] for doc in catalog}
    assert "ARCH-001" in doc_ids
    assert "ARCH-002" in doc_ids
    assert "ARCH-003" in doc_ids
    assert "API-001" in doc_ids
    assert "SCALE-001" in doc_ids
    assert "SEC-001" in doc_ids
    assert "DATA-001" in doc_ids

    # Check chunks structure
    chunks = get_all_indexed_chunks()
    assert len(chunks) > 0
    for chunk in chunks[:5]:
        assert "document_id" in chunk
        assert "breadcrumb" in chunk
        assert "keywords" in chunk
        assert len(chunk["breadcrumb"]) > 0


def test_rag_api_endpoints():
    client = TestClient(app)
    
    # Test /rag/documents
    resp_docs = client.get("/api/v1/rag/documents")
    assert resp_docs.status_code == 200
    docs = resp_docs.json()
    assert len(docs) >= 7

    # Test /rag/chunks
    resp_chunks = client.get("/api/v1/rag/chunks")
    assert resp_chunks.status_code == 200
    chunks = resp_chunks.json()
    assert len(chunks) > 0

    # Test /rag/qdrant-info
    resp_qdrant = client.get("/api/v1/rag/qdrant-info")
    assert resp_qdrant.status_code == 200
    qdrant = resp_qdrant.json()
    assert "collection_name" in qdrant
    assert qdrant["vector_dimension"] == 384
    assert "dashboard_url" in qdrant
