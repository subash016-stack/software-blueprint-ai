# Module 4: Academic RAG Knowledge System

## 1. RAG System Design

The RAG (Retrieval-Augmented Generation) layer anchors architectural recommendations in peer-reviewed literature, established standards (IEEE 830, ISO/IEC/IEEE 29148, ISO/IEC 25010), and proven architectural patterns.

```
  [Knowledge Corpus (knowledge/)]
  • architecture/
  • databases/
  • scalability/
  • security/
  • api/
  • testing/
  • software_engineering/
               │
               ▼
   [Document Ingestion & Chunking]
   • Header-aware markdown splitting (500–1000 chars)
               │
               ▼
   [Local Vector Embeddings]
   • qwen3-embedding:0.6b (1024-dim vectors)
   • SHA-256 Vector Cache
               │
               ▼
   [Vector Store: Qdrant / In-Memory]
   • Cosine similarity search (Top-K = 5)
               │
               ▼
   [Evidence Grounding Engine]
   • Cosine Similarity Scoring
   • Architectural Citation Generation (EVID-001..n)
```

---

## 2. Knowledge Base Structure

The knowledge base is organized into curated domains under `knowledge/`:

| Directory | Documents | Topics Covered |
|---|---|---|
| `architecture/` | `clean_architecture.md`, `event_driven.md`, `microservices.md`, `layered.md` | Domain decoupling, Saga pattern, CQRS, dependency inversion |
| `databases/` | `relational_vs_nosql.md`, `indexing_and_sharding.md` | ACID vs BASE, B-Tree indexing, partition strategies |
| `scalability/` | `caching_strategies.md`, `load_balancing.md` | Cache-Aside, Write-Through, Redis LRU, consistent hashing |
| `security/` | `api_security.md`, `authentication_authorization.md` | OAuth2, JWT with RS256, RBAC, Rate Limiting, OWASP Top 10 |
| `api/` | `rest_vs_graphql.md`, `api_versioning.md` | REST Level 3 HATEOAS, GraphQL federation, URI versioning |
| `testing/` | `testing_pyramid.md` | Unit/Integration/E2E ratio, contract testing, mock isolation |
| `software_engineering/` | `traceability.md`, `change_management.md` | Traceability DAGs, Blast Radius impact analysis |

---

## 3. Evidence-Grounded Recommendations

Each recommendation produced by the RAG Agent contains:
- **`recommendation`**: Architectural decision (e.g., Event-Driven Saga Pattern).
- **`rationale`**: Technical justification grounded in system characteristics.
- **`evidence_id`**: Deterministic citation ID (e.g., `EVID-001`).
- **`source_title` & `section`**: Origin document and section name.
- **`similarity_score`**: Measured cosine similarity score ($0.0 \le \text{score} \le 1.0$).
- **`retrieved_text`**: Verbatim excerpt from literature used to justify the choice.

If no knowledge chunk matches above threshold ($0.45$), `evidence_status = "insufficient"` is declared rather than fabricating citations.
