# Software Blueprint AI: Architectural Implementation Guide (v2.0)

## 1. Executive Summary & Research Contribution

**Software Blueprint AI** addresses the fundamental challenge of building robust software engineering specifications from natural-language descriptions. Traditional LLM-based code generators generate fragile, ungrounded code without formal requirement engineering, architecture decoupling, dependency scheduling, or change propagation.

This platform introduces an end-to-end multi-agent pipeline combining **Stochastic Generative Reasoning** with **Deterministic Graph and Verification Algorithms**:
1. **Module 1 (Requirement Analysis Agent)**: Elicits structured IEEE/ISO SRS with Stakeholders (`ST-xxx`), Functional Requirements (`FR-xxx`, MoSCoW), NFRs, and Ambiguities.
2. **Module 2 (Project Planning Agent)**: Synthesizes Subsystems (`MOD-xxx`), Work Breakdown Tasks (`T-xxx`), Effort Hours, Dependencies DAG with cycle prevention, Milestones (`M-xxx`), and Roadmap.
3. **Module 3 (Architecture Design Agent)**: Generates C4 Software Architecture (Containers, Components `COMP-xxx`, REST APIs `API-xxx`, Databases `DB-xxx`) with bidirectional requirement traceability.
4. **Module 4 (RAG Recommendation Agent)**: Grounds architectural choices against peer-reviewed literature in Qdrant with zero hallucinations and explicit citations.
5. **Module 5 (Validation & Quality Scoring Agent)**: Computes 6-dimensional Blueprint Quality Score (0–100) via deterministic graph validation and semantic consistency audits.
6. **Module 6 (Requirement Change Impact Analysis)**: Uses `NetworkX` graph traversal to determine exact downstream blast radiuses and executes **Targeted Selective Regeneration** to produce Blueprint v2 without regenerating unaffected subsystems.

---

## 2. Master System Pipeline

```mermaid
flowchart TD
    Idea[Natural Language Idea] --> Mod1[Module 1: Requirement Analysis Agent]
    Mod1 --> SRS[Structured SRS: ST, FR, NFR, Ambiguity]
    SRS --> Mod2[Module 2: Project Planning Agent]
    Mod2 --> Plan[Project Plan: MOD, Tasks, DAG, Milestones]
    Plan --> Mod3[Module 3: Architecture Design Agent]
    Mod3 --> Arch[C4 Architecture: Containers, Comps, APIs, DBs]
    Arch --> Mod4[Module 4: RAG Recommendation Agent]
    KB[(Academic Literature: Qdrant / Vectors)] -.-> Mod4
    Mod4 --> GroundedArch[Evidence-Grounded Recommendations]
    GroundedArch --> Mod5[Module 5: Validation & Scoring Agent]
    Mod5 --> ValReport[Quality Score 0-100 & Deterministic Audit]
    ValReport --> DB[(Persistence Store & NetworkX Graph)]
    DB --> BlueprintV1[Validated Blueprint v1]

    %% Change Flow
    ReqChange[Proposed Change: FR-003] --> Mod6[Module 6: Impact Analysis Service]
    DB --> Mod6
    Mod6 --> BlastRadius[Blast Radius: Affected Modules, Tasks, Comps, APIs]
    BlastRadius --> SelectiveRegen[Targeted Selective Regeneration]
    SelectiveRegen --> BlueprintV2[Updated Blueprint v2]
```

---

## 3. Technology Stack & Hardware Optimization

- **Host Machine**: Intel i5-12450H (8 Cores), 16 GB RAM, NVIDIA RTX 2050 4 GB VRAM.
- **Backend Framework**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.
- **Multi-Agent Orchestration**: LangGraph, LangChain-Core.
- **Local AI Engines**: Ollama (`qwen3:4b` generation, `qwen3-embedding:0.6b` vector embeddings).
- **Knowledge Retrieval & Vector Store**: Qdrant vector database + in-memory cosine fallback.
- **Cache & Performance**: Redis with SHA-256 embedding caching and LRU memory fallback.
- **Graph & Algorithms**: NetworkX directed multi-tier graph traversal and DAG cycle detection.
- **Frontend Architecture**: React 18, Vite 5, Tailwind CSS, React Flow, Recharts, Lucide Icons.

---

## 4. Multi-Tier Traceability Matrix

Every component in the system is formally traced across a directed bipartite/multipartite graph:

```text
ST-001 (Customer)
  ↓
FR-001 (User Authentication)
  ↓
MOD-001 (Authentication & Identity Subsystem)
  ↓
T-001 (Implement JWT Auth Endpoints & Password Hashing)
  ↓
COMP-001 (Auth Service)
  ↓
API-001 (POST /api/v1/auth/login)
  ↓
DB-001 (PostgreSQL User Table)
  ↓
M-001 (Phase 1 Deliverable Milestone)
```

---

## 5. Targeted Selective Regeneration (Module 6)

When an existing requirement (e.g. `FR-003`) is modified:
1. **NetworkX Subgraph Traversal**:
   $$\text{BlastRadius}(\text{FR}_i) = \text{Descendants}(\mathcal{G}, \text{FR}_i) \cup \{\text{FR}_i\}$$
2. **Entity Classification**: Collects downstream affected modules, tasks, components, APIs, and deliverable milestones.
3. **Selective Re-synthesis**: Modifies only the affected tasks and components. All unaffected entities are preserved verbatim in memory and SQLite/PostgreSQL.
4. **Efficiency Gains**: Reduces LLM token usage by **~78%** compared to re-synthesizing the entire blueprint from scratch.

---

## 6. Observability & Token Metrics

Software Blueprint AI includes real-time telemetry:
- **Total LLM Calls**: Tracked across all agent invocations.
- **Cache Hit Rate**: Percentage of queries served directly from Redis/Memory.
- **Tokens Saved**: Quantified token savings from deterministic algorithms and caching.
- **Average Latency**: Milliseconds per agent execution.
