"""RAG subsystem module."""

from app.rag.embeddings import get_embedding
from app.rag.qdrant_client import vector_store
from app.rag.retriever import retrieve_relevant_evidence, load_and_ingest_knowledge_base

__all__ = [
    "get_embedding",
    "vector_store",
    "retrieve_relevant_evidence",
    "load_and_ingest_knowledge_base"
]
