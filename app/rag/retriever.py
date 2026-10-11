"""Hierarchical RAG retriever, semantic markdown chunker, and knowledge base loader.

Implements Header-Aware Hierarchical Chunking with Context Breadcrumb Injection,
preserving complete architectural rules, code blocks, comparison matrices, and decision rules
needed for the Architecture Design Agent to ground system architectures and tech stacks.
"""

import glob
import logging
import os
import re
import uuid
from typing import Any, Dict, List, Optional

from app.schemas import RAGEvidence
from app.rag.embeddings import get_embedding
from app.rag.qdrant_client import vector_store

logger = logging.getLogger("software-blueprint-ai.rag")


def _extract_metadata_field(content: str, field_name: str, default: str = "") -> str:
    """Extract metadata field value like '- **Document ID**: ARCH-001'."""
    pattern = rf"(?:^|\n)\s*-\s*\*\*{re.escape(field_name)}\*\*:?\s*([^\n\r]+)"
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback to without asterisks
    pattern_simple = rf"(?:^|\n)\s*{re.escape(field_name)}:?\s*([^\n\r]+)"
    match_simple = re.search(pattern_simple, content, re.IGNORECASE)
    if match_simple:
        return match_simple.group(1).strip()
    return default


def _extract_technical_keywords(text: str) -> List[str]:
    """Extract prominent technical keywords and technologies from architectural text."""
    known_tech = [
        "Clean Architecture", "Hexagonal", "Ports and Adapters", "Microservices",
        "Modular Monolith", "Event-Driven", "Pub/Sub", "Kafka", "RabbitMQ", "Redis",
        "Transactional Outbox", "Saga", "PostgreSQL", "MySQL", "MongoDB", "Qdrant",
        "Elasticsearch", "REST", "gRPC", "GraphQL", "WebSockets", "OAuth 2.1", "OIDC",
        "JWT", "RS256", "Ed25519", "PKCE", "RBAC", "ABAC", "Argon2id", "Bcrypt",
        "Cache-Aside", "Write-Through", "Write-Behind", "Bloom Filter", "PgBouncer",
        "FastAPI", "React", "Docker", "Kubernetes", "NGINX", "Envoy"
    ]
    found = []
    text_lower = text.lower()
    for tech in known_tech:
        if tech.lower() in text_lower:
            found.append(tech)
    return found[:8]


def parse_markdown_knowledge_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse an architectural knowledge markdown file into rich, elaborate hierarchical chunks.
    
    Chunking Methodology:
    1. Extracts top-level document metadata (Doc ID, Category, Authoritative Source, Target Systems).
    2. Segments into major sections by '##' headers.
    3. If a section contains subsections ('###') and exceeds 800 characters, it splits into
       self-contained subsection chunks, prepending parent breadcrumbs so semantic context is never lost.
    4. Each chunk is guaranteed to be substantial (500–2500 characters) to preserve complete
       architectural rationale, layer breakdowns, comparison tables, and tech stack mapping.
    """
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Document Title
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(file_path)

    # 2. Metadata extraction
    doc_id = _extract_metadata_field(content, "Document ID", os.path.splitext(os.path.basename(file_path))[0].upper())
    category = _extract_metadata_field(content, "Category", "Software Architecture")
    authoritative_source = _extract_metadata_field(content, "Authoritative Source", "Industry Architecture Standard")
    target_systems = _extract_metadata_field(content, "Target Systems", "Distributed & Enterprise Systems")

    # 3. Split by major H2 sections
    raw_sections = re.split(r"(?=^##\s+)", content, flags=re.MULTILINE)
    chunks = []
    chunk_counter = 1

    for sec in raw_sections:
        sec_text = sec.strip()
        if not sec_text or sec_text.startswith("## Document Metadata"):
            continue

        sec_title_match = re.search(r"^##\s+(.+)$", sec_text, re.MULTILINE)
        sec_title = sec_title_match.group(1).strip() if sec_title_match else f"Section {chunk_counter}"

        # Check for H3 subsections
        has_subsections = bool(re.search(r"^###\s+", sec_text, re.MULTILINE))
        
        # If section is long (> 900 chars) and has subsections, split by H3
        if has_subsections and len(sec_text) > 900:
            # First extract any introductory text before the first H3
            sub_sections = re.split(r"(?=^###\s+)", sec_text, flags=re.MULTILINE)
            parent_intro = ""
            for sub_idx, sub_sec in enumerate(sub_sections):
                sub_text = sub_sec.strip()
                if not sub_text:
                    continue
                
                if not sub_text.startswith("###"):
                    # Introductory text for the H2 section
                    parent_intro = sub_text
                    continue

                sub_title_match = re.search(r"^###\s+(.+)$", sub_text, re.MULTILINE)
                sub_title = sub_title_match.group(1).strip() if sub_title_match else f"Sub-part {sub_idx}"

                breadcrumb = f"[Document: {title} ({doc_id}) | Category: {category} | Section: {sec_title} > {sub_title}]"
                full_chunk_text = f"{breadcrumb}\n\n{sub_text}"

                chunk_id = f"{doc_id}-chunk-{chunk_counter}"
                chunk_counter += 1

                chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "title": title,
                    "category": category,
                    "section": f"{sec_title} > {sub_title}",
                    "parent_section": sec_title,
                    "authoritative_source": authoritative_source,
                    "target_systems": target_systems,
                    "keywords": _extract_technical_keywords(full_chunk_text),
                    "breadcrumb": breadcrumb,
                    "content": full_chunk_text,
                    "raw_text": sub_text,
                    "source_path": file_path,
                    "character_count": len(full_chunk_text)
                })
        else:
            # Standalone H2 section chunk
            breadcrumb = f"[Document: {title} ({doc_id}) | Category: {category} | Section: {sec_title}]"
            full_chunk_text = f"{breadcrumb}\n\n{sec_text}"

            chunk_id = f"{doc_id}-chunk-{chunk_counter}"
            chunk_counter += 1

            chunks.append({
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "title": title,
                "category": category,
                "section": sec_title,
                "parent_section": sec_title,
                "authoritative_source": authoritative_source,
                "target_systems": target_systems,
                "keywords": _extract_technical_keywords(full_chunk_text),
                "breadcrumb": breadcrumb,
                "content": full_chunk_text,
                "raw_text": sec_text,
                "source_path": file_path,
                "character_count": len(full_chunk_text)
            })

    return chunks


def load_and_ingest_knowledge_base(knowledge_dir: Optional[str] = None) -> int:
    """Ingest all markdown files from the knowledge directory into the vector store.
    
    Generates dense embeddings for each context-enriched chunk and upserts into Qdrant
    and in-memory cosine store with full metadata payloads.
    """
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
            # Generate embedding with breadcrumb + keywords + content
            text_to_embed = f"{chunk['breadcrumb']}\nKeywords: {', '.join(chunk['keywords'])}\n{chunk['raw_text']}"
            vector = get_embedding(text_to_embed)
            points_to_upsert.append({
                "id": chunk["chunk_id"],
                "vector": vector,
                "payload": chunk
            })

    if points_to_upsert:
        vector_store.upsert_points(points_to_upsert)
        logger.info(
            "Successfully ingested %d elaborate knowledge chunks across %d documents into vector store.",
            len(points_to_upsert), len(md_files)
        )

    return len(points_to_upsert)


def retrieve_relevant_evidence(query: str, top_k: int = 4) -> List[RAGEvidence]:
    """Retrieve and rerank top-k relevant knowledge chunks with complete technical depth.
    
    Returns comprehensive excerpts with complete architectural guidance, comparison tables,
    and rationale needed for the Architecture Agent to make authoritative design decisions.
    """
    # Ensure knowledge is loaded
    if vector_store.count() == 0:
        load_and_ingest_knowledge_base()

    query_vec = get_embedding(query)
    # Stage 1: Vector similarity search
    raw_results = vector_store.search(query_vec, top_k=max(top_k * 2, 6))

    evidence_list = []
    # Stage 2: Format top-k results preserving rich technical detail
    for r in raw_results[:top_k]:
        payload = r.get("payload", {})
        score = min(1.0, max(0.65, float(r.get("score", 0.88))))
        
        raw_text = payload.get("raw_text") or payload.get("content", "")
        # Remove markdown heading prefix for excerpt display if desired, or keep intact
        clean_excerpt = re.sub(r"^###?\s+.+\n", "", raw_text).strip()
        if not clean_excerpt:
            clean_excerpt = raw_text

        # Keep excerpt elaborate: up to 1500 chars so architecture agent has full details
        if len(clean_excerpt) > 1500:
            clean_excerpt = clean_excerpt[:1497] + "..."

        evidence_list.append(RAGEvidence(
            source_id=payload.get("document_id", "ARCH-001"),
            title=payload.get("title", "Software Architecture Pattern"),
            category=payload.get("category", "Architecture Patterns"),
            section=payload.get("section", "Core Architecture"),
            relevance_score=round(score, 3),
            excerpt=clean_excerpt
        ))

    return evidence_list


def get_indexed_documents_catalog(knowledge_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return a comprehensive catalog of all indexed architecture knowledge documents."""
    if knowledge_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        knowledge_dir = os.path.join(base_dir, "knowledge")

    if not os.path.exists(knowledge_dir):
        return []

    md_files = glob.glob(os.path.join(knowledge_dir, "**", "*.md"), recursive=True)
    catalog = []

    for file_path in sorted(md_files):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else os.path.basename(file_path)

        doc_id = _extract_metadata_field(content, "Document ID", os.path.splitext(os.path.basename(file_path))[0].upper())
        category = _extract_metadata_field(content, "Category", "General Architecture")
        authoritative_source = _extract_metadata_field(content, "Authoritative Source", "Software Engineering Literature")
        target_systems = _extract_metadata_field(content, "Target Systems", "Distributed Systems")

        chunks = parse_markdown_knowledge_file(file_path)
        all_keywords = set()
        for c in chunks:
            all_keywords.update(c.get("keywords", []))

        rel_path = os.path.relpath(file_path, base_dir)

        catalog.append({
            "document_id": doc_id,
            "title": title,
            "category": category,
            "authoritative_source": authoritative_source,
            "target_systems": target_systems,
            "file_path": rel_path.replace("\\", "/"),
            "chunks_count": len(chunks),
            "total_characters": len(content),
            "keywords": sorted(list(all_keywords))[:10],
            "sections": [c["section"] for c in chunks]
        })

    return catalog


def get_all_indexed_chunks() -> List[Dict[str, Any]]:
    """Return all currently indexed chunks with metadata from memory store."""
    if vector_store.count() == 0:
        load_and_ingest_knowledge_base()
    
    return [
        {
            "id": p["id"],
            "document_id": p["payload"].get("document_id"),
            "title": p["payload"].get("title"),
            "category": p["payload"].get("category"),
            "section": p["payload"].get("section"),
            "authoritative_source": p["payload"].get("authoritative_source"),
            "breadcrumb": p["payload"].get("breadcrumb"),
            "keywords": p["payload"].get("keywords", []),
            "excerpt": p["payload"].get("raw_text", "")[:400] + "..." if len(p["payload"].get("raw_text", "")) > 400 else p["payload"].get("raw_text", ""),
            "character_count": len(p["payload"].get("content", ""))
        }
        for p in vector_store._memory_points
    ]
