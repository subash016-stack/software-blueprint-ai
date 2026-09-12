# Module 3 & System Architecture Design

## 1. System Overview

Software Blueprint AI employs a decoupled, multi-agent orchestration architecture built with **LangGraph**, **FastAPI**, **Pydantic v2**, and local **Ollama** LLM inference.

```
                    Natural Language Idea
                              │
                              ▼
                  [Requirement Agent (M1)]
                  • IEEE 830/29148 SRS Synthesis
                  • Stakeholders, FRs, NFRs, MoSCoW
                              │
                              ▼
                  [Project Planning Agent (M2)]
                  • Work Breakdown Structure (WBS)
                  • Tasks, Dependencies, Milestones
                              │
                              ▼
                  [Architecture Agent (M3)]
                  • C4 Containers & Components
                  • REST APIs & DB Schemas
                  • Architecture Decision Records (ADRs)
                              │
                              ▼
                  [RAG Evidence Layer (M4)]
                  • Qdrant Vector Semantic Retrieval
                  • Academic Grounding & Confidence Scores
                              │
                              ▼
                  [Validation Agent (M5)]
                  • NetworkX DAG Cycle Audit & Repair
                  • Traceability Coverage Audit (0–100)
                              │
                              ▼
              [Impact Analysis & Versioning (M6)]
                  • Blast Radius Graph Traversal
                  • Targeted Selective Regeneration (v1 ➔ v2)
```

---

## 2. Module 3: Architecture Design Agent

The Architecture Agent consumes the validated outputs of **Module 1 (SRS)** and **Module 2 (Project Plan)**. It does not re-interpret the raw prompt; instead, it synthesizes a structured, deployable architecture that maintains strict backward traceability.

### 2.1 C4 Component Model
Every architecture component follows deterministic naming conventions:
- **Containers**: `CONT-001`, `CONT-002` (e.g., Web App, API Gateway, Background Worker)
- **Components**: `COMP-001`, `COMP-002` (e.g., Auth Service, Payment Processor)
- **APIs**: `API-001`, `API-002` (Method, Path, Request/Response Payload schema)
- **Databases**: `DB-001`, `DB-002` (Type, Engine, Relational/Document Tables, Indices)
- **External Systems**: `EXT-001` (Stripe, GitHub Webhooks, SendGrid, etc.)

---

## 3. Architecture Decision Records (ADRs)

For each architectural decision (e.g., Database choice, Communication pattern, Authentication mechanism), the system generates a formal ADR:

```json
{
  "id": "ADR-001",
  "title": "Adoption of PostgreSQL for Core Transactional Persistence",
  "status": "Accepted",
  "context": "Financial ledger and order data require ACID compliance and strong relational foreign key constraints.",
  "decision": "Use PostgreSQL with SQLAlchemy ORM and Alembic migrations.",
  "rationale": "High write-throughput, robust JSONB support, and mature row-level locking.",
  "alternatives": ["MongoDB", "MySQL", "DynamoDB"],
  "rejected_alternatives": [
    "MongoDB: Lacks multi-entity atomic relational constraints by default",
    "DynamoDB: High cost overhead and complex multi-table indexing queries"
  ],
  "consequences": "Requires relational migration management and connection pooling (PgBouncer).",
  "requirement_ids": ["FR-001", "NFR-002"],
  "evidence_ids": ["EVID-003", "EVID-007"],
  "confidence": 0.94
}
```

---

## 4. Local Execution & Efficiency Architecture

1. **Deterministic Offloading**: Graph traversals, cycle detection, and traceability audits run purely in Python (`NetworkX`) in <2ms, bypassing the LLM.
2. **Multi-Tier Caching**: Redis + SHA-256 in-memory LRU cache prevents redundant model invocations.
3. **Structured Pydantic Validation**: Guarantees typed outputs across all agent boundaries with automatic schema retries.
