# Event-Driven Architecture and Asynchronous Messaging

## Document Metadata
- **Document ID**: ARCH-002
- **Category**: Architecture Patterns
- **Section**: Asynchronous Decoupling & Event Brokers
- **Authoritative Source**: Hohpe, G., & Woolf, B. (2003). Enterprise Integration Patterns.

## Core Principle
Event-Driven Architecture (EDA) produces, detects, consumes, and reacts to events across decoupled software services. Rather than executing synchronous RPC calls between microservices, producer components emit domain events (e.g. `OrderPlaced`, `PaymentAuthorized`) to a message broker (Kafka, RabbitMQ, Redis Streams), enabling consumer services to process actions asynchronously.

## Key Benefits & Trade-offs
- **High Scalability & Elasticity**: Peak traffic spikes are absorbed by message queues without cascading service exhaustion.
- **Fault Isolation**: If downstream services experience temporary outages, events remain buffered in the message queue.
- **Eventual Consistency**: Replaces distributed two-phase commit transactions with compensating actions and asynchronous convergence.
