# Modular Monolith vs. Microservices Architecture Guide

## Document Metadata
- **Document ID**: ARCH-003
- **Category**: Architecture Patterns
- **Authoritative Source**: Newman, S. (2021). Monolith to Microservices: Evolutionary Patterns to Transform Your Monolith; Fowler, M. (2015). Microservice Trade-Offs.
- **Target Systems**: Enterprise Web Applications, B2B SaaS, Microservice Migrations, High-Scale Distributed Platforms

---

## 1. Core Architectural Overview

Selecting between a **Modular Monolith** and a **Distributed Microservices Architecture** is one of the most critical structural decisions in software engineering. Making the wrong choice introduces either unmaintainable code entanglement or catastrophic distributed systems operational overhead.

```
+------------------------------------------+    +------------------------------------------+
|            MODULAR MONOLITH              |    |          MICROSERVICES CLUSTER           |
|                                          |    |                                          |
|  [ Auth ] <---> [ Orders ] <---> [ DB ]  |    |  [ Auth Svc ]  --gRPC-->  [ Orders Svc ] |
|     ^               ^                    |    |       |                         |        |
|     +--- In-Memory Function Calls -------+    |   [Auth DB]                 [Orders DB]  |
|                                          |    |     ^ (Network Boundary / API Gateway)   |
|  * Single Deployment Unit                |    |  * Independent Deployable Services       |
|  * Shared Relational ACID Transactions   |    |  * Polyglot Persistence & Isolated Scales|
+------------------------------------------+    +------------------------------------------+
```

---

## 2. Deep-Dive Pattern Breakdown

### A. The Modular Monolith (Recommended Default for Most Applications)
- **Definition**: A single deployable binary or runtime process containing strictly bounded, decoupled internal modules with explicit public interfaces and private internal packages.
- **Communication Mechanism**: In-memory function calls, native language interfaces, and localized event emitters (zero network serialization latency).
- **Data Persistence**: Single shared relational database (PostgreSQL) partitioned into logical schemas per module, enabling atomic ACID transactions when needed.
- **Operational Profile**: Zero container orchestration overhead (runs seamlessly in a single Docker container or basic VM). Rapid CI/CD build times and simplified debugging.

### B. Distributed Microservices Architecture
- **Definition**: A suite of independently deployable, autonomous services grouped around business capabilities. Each service owns its private datastore (Database-per-Service pattern).
- **Communication Mechanism**: High-speed gRPC (binary Protobuf over HTTP/2) for synchronous internal communications, and message brokers (Kafka/RabbitMQ) for asynchronous domain events.
- **Operational Profile**: Requires advanced infrastructure: Kubernetes orchestration, API Gateway (Kong/Envoy), centralized distributed tracing (OpenTelemetry/Jaeger), service mesh (Istio), and decentralized CI/CD pipelines.

---

## 3. Comparative Decision Matrix

| Dimension | Modular Monolith | Distributed Microservices | Selection Guidance |
| :--- | :--- | :--- | :--- |
| **Team Structure** | 1 to 3 engineering teams (< 25 devs) | 4+ independent engineering teams (30+ devs) | Match Conway's Law: Split into microservices only when independent team deployment velocity is constrained. |
| **Data Consistency**| Strict ACID relational integrity | Eventual consistency via Saga pattern | Choose Monolith if cross-entity foreign keys and atomic multi-table rollbacks are vital. |
| **Operational Cost**| Very low ($10 - $100/mo) | High ($500 - $5,000+/mo for K8s, tracing, monitoring) | Monolith minimizes cloud spend for early-to-mid stage systems. |
| **Network Latency** | Sub-microsecond (in-memory pointer calls)| 2 - 20 ms per cross-service network hop | Monolith eliminates the N+1 network call problem across service boundaries. |
| **Deployability** | Single all-or-nothing pipeline | Independent service rollouts & canary deploys | Microservices allow deploying Order Service without restarting Auth Service. |
| **Fault Blast Radius**| Process crash can bring down the server | Failure in one service is isolated by circuit breakers | Use circuit breakers (Resilience4j/pybreaker) in microservices. |

---

## 4. Technology Stack Recommendations by Architecture

### For Modular Monolith:
- **Language / Framework**: Python 3.11+ (FastAPI), TypeScript (NestJS), or Go.
- **Architecture Pattern**: Clean Architecture with strict module directory isolation:
  ```
  app/
    modules/
      auth/       --> domain, use_cases, adapters
      catalog/    --> domain, use_cases, adapters
      billing/    --> domain, use_cases, adapters
  ```
- **Database**: PostgreSQL 16 with modular schemas (`auth_schema`, `billing_schema`).
- **Cache**: Redis 7 for session cache and in-memory pub/sub.

### For Microservices Architecture:
- **API Gateway**: Envoy, Kong, or Traefik for TLS termination, routing, and rate limiting.
- **Inter-Service Communication**: gRPC with Protocol Buffers for fast binary serialization.
- **Event Bus**: Apache Kafka or RabbitMQ for domain events.
- **Observability**: OpenTelemetry SDK + Prometheus metrics + Grafana dashboard.
- **Persistence**: Database-per-Service (e.g. Auth Service &rarr; PostgreSQL, Analytics &rarr; ClickHouse).

---

## 5. Architectural Decision Rules for AI Agents

1. **Rule of Default**: Default to a **Modular Monolith** unless explicit user requirements mandate independent scaling or multi-team organizational boundaries.
2. **Rule of Data Coupling**: If the requirements demand complex relational joins, atomic transaction rollbacks across entities, or immediate consistency, choose a **Modular Monolith**.
3. **Rule of Polyglot Scale**: If one component requires 100x higher throughput than others (e.g., real-time video stream ingestion vs account settings CRUD), isolate that single component as a specialized microservice while keeping the core system modular.
