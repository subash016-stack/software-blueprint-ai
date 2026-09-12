# Caching Topologies and Scalability Patterns

## Document Metadata
- **Document ID**: SCALE-001
- **Category**: Scalability & Caching
- **Section**: Multi-Tier Caching & Read-Replica Sharding
- **Authoritative Source**: Kleppmann, M. (2017). Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems.

## Caching Strategy
1. **Cache-Aside (Lazy Loading)**: Application queries Redis first. On cache miss, fetch from PostgreSQL, write to Redis with TTL, and return.
2. **Write-Through / Invalidation**: When modifying entities, execute transactional DB update and immediately invalidate corresponding cache keys to maintain consistency.
3. **Database Read/Write Splitting**: Route write transactions to the primary database while distributing intensive analytical/read queries across asynchronous read replicas.
4. **Horizontal Scaling**: Stateless backend containers running behind an NGINX / Cloud load balancer with sticky sessions disabled.
