# Database Architecture and Polyglot Persistence Selection Guide

## Document Metadata
- **Document ID**: DATA-001
- **Category**: Database Architecture & Persistence
- **Authoritative Source**: Kleppmann, M. (2017). *Designing Data-Intensive Applications*; PostgreSQL Global Development Group; Stonebraker, M. (2010). *SQL Databases v. NoSQL Databases*; Qdrant Vector Engine Documentation.
- **Target Systems**: Distributed Applications, High-Concurrency Web Applications, Hybrid Analytical & Transactional Systems, AI/RAG Search Pipelines.

---

## 1. Polyglot Persistence Paradigm

Modern production systems rarely rely on a single database engine for all persistence workloads. Polyglot Persistence assigns each distinct data model, read/write profile, and querying requirement to its specialized storage technology.

```
+---------------------------------------------------------------------------------+
|                               API Gateway / Services                            |
+---------------------------------------------------------------------------------+
       |                       |                      |                     |
       v                       v                      v                     v
+---------------+      +---------------+      +---------------+     +---------------+
|  PostgreSQL   |      |  Redis 7+     |      |    Qdrant     |     | Elasticsearch |
| Relational/ACID|      | Key-Value/TTL |      | Dense Vectors |     | Full-Text     |
| Core Entities |      | Sessions/Cache|      | Semantic Search|    | Log Ingestion |
+---------------+      +---------------+      +---------------+     +---------------+
```

---

## 2. Comprehensive Database Engine Comparison

| Database Paradigm | Representative Engines | Best-Fit Workloads | Query Capabilities | Consistency Guarantee |
| :--- | :--- | :--- | :--- | :--- |
| **Relational (RDBMS)** | **PostgreSQL 16+**, MySQL 8+ | Transactional business core, accounting, billing, multi-table joins, relational schemas | Full SQL-99, CTEs, Window Functions, ACID transactions, JSONB indexing | Strong Consistency (ACID, Serializable / Read Committed) |
| **Key-Value Store** | **Redis 7+**, Dragonfly, KeyDB | Session management, auth token blacklists, fast counters, Pub/Sub channels, cache tiers | Key lookup, Hash, Set, Sorted Set (ZSET), Bitmaps, Streams | In-memory with optional persistence (AOF/RDB); eventual for replicas |
| **Vector Database** | **Qdrant**, Milvus, pgvector | LLM Retrieval-Augmented Generation (RAG), semantic search, recommendation engines, facial embeddings | Approximate Nearest Neighbors (HNSW), cosine/dot-product similarity, metadata payload filtering | Configurable consistency across replicas; ACID payload filtering |
| **Document Store** | **MongoDB 7+**, DynamoDB | Unstructured event logs, catalogs with dynamic schema, CMS article bodies | Document JSON/BSON querying, aggregation pipelines | Tunable consistency (W:majority, R:majority) |
| **Search Engine** | **Elasticsearch**, OpenSearch, Meilisearch | Fuzzy full-text search, multi-language stemming, inverted index tokenization | BM25 text relevance, faceted search, analytical aggregations | Near real-time index refresh (~1s delay) |

---

## 3. Relational vs. Document Database Decision Framework

### When to Choose PostgreSQL (Default Relational Anchor):
1. **Strict Data Integrity & Foreign Keys**: Relations between users, organizations, subscriptions, projects, and blueprints require strict referential integrity (`ON DELETE CASCADE` / `RESTRICT`).
2. **ACID Transactions**: Financial operations, inventory adjustments, and status workflows require multi-statement atomic transactions.
3. **Hybrid JSON Capabilities**: Modern PostgreSQL supports `JSONB` columns with GIN indexing, allowing document-style flexibility without abandoning relational constraints.

### When to Choose Document Store (MongoDB):
1. **Schema Polymorphism**: Highly heterogeneous data structures where each document exhibits radically different fields that cannot be normalized cleanly.
2. **Horizontal Sharding Out of the Box**: Need to distribute massive write throughput across thousands of commodity nodes without complex foreign-key constraints.

---

## 4. Vector Database Architecture: Qdrant

For AI and RAG architectures, traditional relational databases degrade severely when computing vector distance over millions of high-dimensional vectors (e.g., 1024-dim or 1536-dim embeddings).

### Qdrant Architectural Advantages:
- **Rust Implementation**: Predictable, garbage-collection-free performance with zero-copy vector serialization.
- **Hierarchical Navigable Small World (HNSW)**: Graph-based approximate nearest neighbor indexing achieving sub-5ms retrieval over millions of dense vectors.
- **Payload-Based Filtering**: Combines vector similarity with strict metadata filtering in a single graph traversal step (e.g., filter by `category = "architecture_patterns"` while computing cosine similarity).
- **Web UI & REST/gRPC API**: Native web dashboard at port `6333` and high-performance gRPC at port `6334`.

---

## 5. Connection Pooling and Operational Resilience

- **Database Connection Pooling**:
  - Direct database connections consume 2MB–10MB of RAM per connection on PostgreSQL. Under microservice concurrency, this leads to connection exhaustion.
  - Implement external pooling via **PgBouncer** (Transaction pooling mode) or internal application pooling (e.g., `asyncpg` pool with `min_size=5, max_size=20`).
- **Read-Write Splitting**:
  - Writes route to the primary read-write replica.
  - Heavy read and analytical queries route to asynchronous read replicas via connection string routing or proxy (AWS Aurora Read Replicas / HAProxy).

---

## 6. Decision Rules for Architecture Agent
- Select **PostgreSQL 16** as the default primary relational datastore for all structured business entities.
- Select **Redis 7.x** for session management, fast caching, and rate limiting counters.
- Select **Qdrant** as the dedicated vector datastore for semantic search and RAG knowledge retrieval.
- Create an Architectural Decision Record (ADR) citing `DATA-001` justifying **Polyglot Persistence with PostgreSQL, Redis, and Qdrant**.
