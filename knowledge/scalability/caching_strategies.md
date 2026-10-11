# Caching Topologies and Scalability Patterns

## Document Metadata
- **Document ID**: SCALE-001
- **Category**: Scalability & Caching
- **Authoritative Source**: Kleppmann, M. (2017). *Designing Data-Intensive Applications*; Redis Open Source Architecture Guidelines; RFC 7234 (HTTP/1.1 Caching).
- **Target Systems**: High-throughput web applications, REST/GraphQL microservices, high-concurrency SaaS, low-latency transaction processing engines.

---

## 1. Core Caching Topologies & Write Strategies

In high-scale systems, caching reduces I/O pressure on relational and document datastores, cuts P99 response latencies from 80ms to <3ms, and protects primary transactional databases from query saturation.

### 1.1 Cache-Aside (Lazy Loading)
- **Workflow**:
  1. Application receives a query (e.g., `GET /api/v1/blueprints/{id}`).
  2. Query Redis cache for key `blueprint:{id}`.
  3. **Cache Hit**: Deserialize JSON / Protobuf payload and return immediately.
  4. **Cache Miss**: Fetch from primary database (PostgreSQL/MySQL), write record to Redis with an explicit TTL (Time-To-Live), and return to client.
- **Pros**: Only requested entities occupy memory; cache failures do not crash the system (degrades gracefully to DB queries).
- **Cons**: Cache miss penalty on cold starts; possibility of stale data if mutations bypass cache invalidation.

### 1.2 Write-Through & Write-Behind (Write-Back)
- **Write-Through**: The application writes synchronously to the cache, and the cache engine immediately persists to the database before acknowledging. Guarantees consistency at the cost of higher write latency.
- **Write-Behind (Write-Back)**: The application writes exclusively to the cache, which acknowledges immediately. An asynchronous background worker batches updates and flushes them to the persistent database. Maximizes write throughput; introduces risk of data loss if the cache node crashes before flushing.

### 1.3 Cache Invalidation Strategies
- **TTL with Jitter**: Avoid cache stampedes (thundering herds) by adding random variance to expiration times (e.g., `base_ttl = 3600s + uniform_random(-300, 300)s`).
- **Event-Driven Invalidation**: When a mutation occurs (e.g., `UpdateBlueprintCommand`), emit an invalidation event via Redis Pub/Sub or transactional outbox to purge exact keys or tag-based sets (`blueprint:{id}`).
- **Two-Phase Eviction**: Soft TTL and hard TTL. When soft TTL expires, serve stale data while a background coroutine asynchronously refreshes the cache from the database.

---

## 2. Advanced Caching Patterns & Failure Mitigations

| Failure Mode | Mechanism | Mitigation Technique |
| :--- | :--- | :--- |
| **Cache Stampede (Thundering Herd)** | Thousands of concurrent requests hit a popular key at the exact moment its TTL expires, overwhelming the DB. | **Mutex / Distributed Lock** (`SETNX` with TTL) so only one worker queries the DB while others wait, or use **Probabilistic Early Recomputation (XFetch)**. |
| **Cache Penetration** | Clients request keys that do not exist in the database, causing every request to bypass cache and hit DB. | Cache `null` values with a short TTL (e.g., 60 seconds), or place a **Bloom Filter** in front of the cache to quickly reject non-existent IDs. |
| **Cache Avalanche** | Redis instance restarts or a large proportion of keys expire simultaneously, shifting all traffic to DB. | Cluster Redis with active replication across AZs; stagger expiration TTLs; enforce Circuit Breakers in API gateway. |

---

## 3. Technology Stack & Multi-Tier Caching Hierarchy

A production-grade architecture leverages a multi-tiered hierarchy:

1. **Client & CDN Edge Tier (Cloudflare / CloudFront)**:
   - Cache static assets, bundle scripts, and cacheable HTTP responses via `Cache-Control: public, max-age=31536000, immutable`.
   - Stale-While-Revalidate headers for semi-dynamic read endpoints.
2. **Reverse Proxy / Gateway Tier (NGINX / Envoy)**:
   - Micro-caching (1–5 second TTL) for unauthenticated public listing pages to absorb traffic surges.
3. **Application Distributed Memory Tier (Redis 7+ / Dragonfly / KeyDB)**:
   - Primary operational cache for sessions, user permissions, hot entity DTOs, and rate limiting counters.
   - Redis cluster with Sentinel or Raft-based consensus for automatic failover.
4. **Local In-Process Tier (LRU Cache / Caffeine / Python `functools.lru_cache`)**:
   - Ultra-low latency (<100 nanoseconds) for static configuration constants and authorization role hierarchies.

---

## 4. Architectural Decision Matrix

- **Choose Cache-Aside with Redis**: For read-heavy applications (80%+ reads), e-commerce catalog browsing, user profile lookups, and session tokens.
- **Choose Read-Replica Sharding**: When dataset size exceeds RAM budget, or complex SQL analytical aggregations and sorting are required that Redis cannot natively evaluate.
- **Choose Multi-Tier CDN + Redis**: For globally distributed consumer web applications requiring sub-50ms TTFB across geographical regions.

---

## 5. Decision Rules for Architecture Agent
- When planning scalable web architectures, prescribe **Redis 7.x** as the caching tier.
- Always include an operational connection pooling configuration (e.g., `redis-py` ConnectionPool or Lettuce for Java).
- Pair with an ADR detailing **Cache-Aside Pattern with Randomized TTL and Distributed Lock Mutex** to guarantee database protection.
