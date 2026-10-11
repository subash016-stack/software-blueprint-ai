# Event-Driven Architecture and Asynchronous Messaging

## Document Metadata
- **Document ID**: ARCH-002
- **Category**: Architecture Patterns
- **Authoritative Source**: Hohpe, G., & Woolf, B. (2003). Enterprise Integration Patterns; Kleppmann, M. (2017). Designing Data-Intensive Applications.
- **Target Systems**: Distributed Microservices, High-Throughput Telemetry, E-Commerce, IoT Fleets, Real-Time Financial Transactions

---

## 1. Core Architectural Principle
Event-Driven Architecture (EDA) structures software systems around the production, detection, publication, and consumption of immutable domain events. Components communicate asynchronously without direct peer-to-peer coupling:

```
[Producer Service] 
       │ (1. Emits 'OrderCreated' Event)
       ▼
┌──────────────────────────────────────────────┐
│  Message Broker / Event Stream (Kafka/Redis) │
└──────┬───────────────────────┬───────────────┘
       │                       │
       ▼ (Asynchronous)        ▼ (Asynchronous)
[Inventory Service]     [Notification Worker]
```

Unlike synchronous request-response protocols (HTTP/REST, gRPC) where a failure in the downstream service immediately cascades back to the caller, EDA establishes temporal decoupling—producers emit events and immediately resume execution without waiting for downstream processing.

---

## 2. Core Messaging Patterns & Architectural Primitives

### A. Publish-Subscribe (Pub/Sub)
- **Concept**: Publishers broadcast events to a named topic or exchange without knowing which subscribers (if any) exist.
- **Use Case**: Domain event notifications (e.g., `UserRegisteredEvent`, `ConsultationBookedEvent`) ingested by multiple independent subsystems (Analytics, Email Service, CRM).

### B. Competing Consumers (Worker Queues)
- **Concept**: Multiple worker processes read from a shared queue; each task/message is delivered to and processed by exactly one available worker.
- **Use Case**: Heavy compute tasks, video transcoding, PDF generation, AI model batch inference.

### C. The Transactional Outbox Pattern
- **Problem**: Dual-write hazard—writing to a relational database and sending a message to a broker in separate network calls can lead to data inconsistency if one fails.
- **Solution**: Save the domain entity update AND the outgoing event into an `outbox` table in the same local ACID database transaction. A background Debezium CDC (Change Data Capture) process or polling worker reads the outbox table and dispatches events to the message broker with guaranteed at-least-once delivery.

### D. Idempotency & De-duplication
- **Principle**: In distributed systems, network partitions force message brokers to use **at-least-once delivery**. Consumers must be strictly idempotent.
- **Implementation**: Every event carries a unique `idempotency_key` (UUID v4 or deterministic SHA-256 hash). Consumers check a Redis or database uniqueness constraint before applying side effects:
  ```python
  if redis_client.set(f"idemp:{event.id}", "1", nx=True, ex=86400) is None:
      logger.info("Duplicate event %s skipped.", event.id)
      return
  ```

### E. Dead-Letter Queues (DLQ) & Poison Pill Handling
- Messages that fail processing after $N$ retry attempts (with exponential backoff and jitter) are automatically routed to a Dead-Letter Queue (DLQ) for forensic analysis and manual replay, preventing consumer worker pool lockup.

---

## 3. Technology Stack Comparison Matrix: Message Brokers

| Attribute | Redis Streams / PubSub | RabbitMQ (AMQP) | Apache Kafka | AWS SQS / SNS |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Paradigm** | In-memory stream / ephemeral queue | Smart broker, flexible routing | High-throughput distributed log | Managed cloud queue & fanout |
| **Max Throughput** | ~50,000 - 100,000 msg/sec | ~20,000 - 50,000 msg/sec | ~1,000,000+ msg/sec | Scalable cloud limits |
| **Latency Profile** | Sub-millisecond (< 1 ms) | Low (1 - 5 ms) | Low-Medium (5 - 15 ms) | Medium (15 - 40 ms) |
| **Message Retention** | In-memory with RDB/AOF persistence | Deleted upon consumer ACK | Configurable log retention (days/years)| 14-day retention window |
| **Ordering Guarantees**| Per-stream FIFO | Per-queue FIFO | Strict partition key ordering | FIFO queues available |
| **Recommended Use** | Lightweight tasks, real-time caching, websockets | Complex routing, enterprise task queues, microservices | High-scale telemetry, event sourcing, big data | Cloud-native serverless pipelines |

---

## 4. Decision Framework: When to Choose Event-Driven Architecture

### Recommended Scenarios:
1. **High Volume Spikes & Traffic Elasticity**: Ingestion endpoints (e.g., IoT sensor telemetry, Black Friday flash sales) where spikes must be absorbed without overloading backend databases.
2. **Multi-Service Domain Fanout**: When a single business action triggers 3 or more independent downstream reactions (billing, auditing, email, search re-indexing).
3. **Decoupled Service Availability**: When core business capabilities must continue accepting customer requests even when non-critical auxiliary services are offline.

### Anti-Patterns & When to Avoid:
- **Strict Immediate Read-After-Write Consistency**: If the user interface requires an instantaneous synchronous response before rendering the next page, EDA introduces eventual consistency complexities.
- **Simple Single-Container Applications**: Introduces broker operational overhead, distributed tracing requirements, and debugging complexity without tangible architectural benefit.

---

## 5. Architectural Trade-offs & Mitigations

| Quality Attribute | Trade-off Description | Production Mitigation Strategy |
| :--- | :--- | :--- |
| **Consistency** | Eventual consistency means read models may temporarily lag write models. | Display optimistic UI updates; communicate processing state to users. |
| **Observability** | Request flows cross asynchronous broker boundaries, obscuring stack traces. | Propagate W3C Trace Context (`traceparent` header) across all messages. |
| **Complexity** | Distributed transactions cannot use standard database locks. | Implement the **Saga Pattern** with compensating transactions for rollbacks. |
