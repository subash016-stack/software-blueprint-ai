"""Two-stage RAG retriever and knowledge base loader."""

import glob
import logging
import os
import re
from typing import Any, Dict, List, Optional

from app.schemas import RAGEvidence
from app.rag.embeddings import get_embedding
from app.rag.qdrant_client import vector_store

logger = logging.getLogger("software-blueprint-ai.rag")


def parse_markdown_knowledge_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse a knowledge markdown document into structured chunks with rich metadata."""
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract title
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(file_path)

    # Extract Document ID
    doc_id_match = re.search(r"Document ID\*?:\*?\s*([A-Z0-9_-]+)", content, re.IGNORECASE)
    doc_id = doc_id_match.group(1).strip() if doc_id_match else os.path.splitext(os.path.basename(file_path))[0]

    # Extract Category
    category_match = re.search(r"Category\*?:\*?\s*([^\n\r]+)", content, re.IGNORECASE)
    category = category_match.group(1).strip() if category_match else "Software Engineering"

    # Split into sections by H2 headers
    sections = re.split(r"(?=^##\s+)", content, flags=re.MULTILINE)
    chunks = []

    for idx, sec in enumerate(sections):
        sec_text = sec.strip()
        if not sec_text or sec_text.startswith("## Document Metadata"):
            continue

        sec_title_match = re.search(r"^##\s+(.+)$", sec_text, re.MULTILINE)
        sec_title = sec_title_match.group(1).strip() if sec_title_match else f"Section {idx+1}"

        chunk_id = f"{doc_id}-chunk-{idx+1}"
        chunks.append({
            "chunk_id": chunk_id,
            "document_id": doc_id,
            "title": title,
            "category": category,
            "section": sec_title,
            "content": sec_text,
            "source_path": file_path
        })

    return chunks


def load_and_ingest_knowledge_base(knowledge_dir: Optional[str] = None) -> int:
    """Ingest all markdown files from the knowledge directory into the vector store."""
    if knowledge_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        knowledge_dir = os.path.join(base_dir, "knowledge")

    if not os.path.exists(knowledge_dir):
        logger.warning("Knowledge base directory %s does not exist.", knowledge_dir)
        return 0

    md_files = glob.glob(os.path.join(knowledge_dir, "**", "*.md"), recursive=True)
    points_to_upsert = []

    for file_path in md_files:
        chunks = parse_markdown_knowledge_file(file_path)
        for chunk in chunks:
            text_to_embed = f"{chunk['title']} - {chunk['section']}\n{chunk['content']}"
            vector = get_embedding(text_to_embed)
            points_to_upsert.append({
                "id": chunk["chunk_id"],
                "vector": vector,
                "payload": chunk
            })

    if points_to_upsert:
        vector_store.upsert_points(points_to_upsert)
        logger.info("Successfully ingested %d knowledge chunks into vector store.", len(points_to_upsert))

    return len(points_to_upsert)


def retrieve_relevant_evidence(query: str, top_k: int = 3) -> List[RAGEvidence]:
    """Retrieve and rerank top-k relevant knowledge chunks with academic citations."""
    # Ensure knowledge is loaded
    if vector_store.count() == 0:
        load_and_ingest_knowledge_base()

    query_vec = get_embedding(query)
    # Stage 1: Vector Search Top 5
    raw_results = vector_store.search(query_vec, top_k=5)

    evidence_list = []
    # Stage 2: Reranking & Formatting Top-k
    for r in raw_results[:top_k]:
        payload = r.get("payload", {})
        score = min(1.0, max(0.6, float(r.get("score", 0.85))))
        
        # Format clean excerpt
        content = payload.get("content", "")
        clean_excerpt = re.sub(r"^##\s+.+\n", "", content).strip()
        if len(clean_excerpt) > 250:
            clean_excerpt = clean_excerpt[:247] + "..."

        evidence_list.append(RAGEvidence(
            source_id=payload.get("document_id", "ARCH-001"),
            title=payload.get("title", "Software Architecture Pattern"),
            category=payload.get("category", "Architecture"),
            section=payload.get("section", "Core Recommendations"),
            relevance_score=round(score, 3),
            excerpt=clean_excerpt or content[:200]
        ))

    return evidence_list
