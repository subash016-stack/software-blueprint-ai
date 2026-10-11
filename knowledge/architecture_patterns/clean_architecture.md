# Clean and Hexagonal Architecture Pattern

## Document Metadata
- **Document ID**: ARCH-001
- **Category**: Architecture Patterns
- **Authoritative Source**: Martin, R. C. (2017). Clean Architecture: A Craftsman's Guide to Software Structure and Design; Cockburn, A. (2005). Hexagonal Architecture (Ports and Adapters).
- **Target Systems**: Modular Monoliths, Microservices, Domain-Centric SaaS Applications, Critical Financial & Healthcare Systems

---

## 1. Core Architectural Principle & Dependency Inversion
Clean Architecture organizes software into concentric, decoupled rings where core business domain logic remains strictly isolated from user interfaces, external transport protocols, database engines, third-party SDKs, and infrastructure frameworks.

The fundamental governing law is the **Dependency Inversion Principle (DIP)**:
> *Source code dependencies must point solely inward toward higher-level domain policies. No inner circle can know anything about an outer circle—including its schemas, class definitions, function calls, or database drivers.*

```
+-------------------------------------------------------------+
| Frameworks & Drivers (FastAPI, React, PostgreSQL, Docker)   |
|   +-------------------------------------------------------+ |
|   | Interface Adapters (Controllers, Gateways, DTOs)     | |
|   |   +-----------------------------------------------+   | |
|   |   | Application Use Cases (Commands, Queries)     |   | |
|   |   |   +---------------------------------------+   |   | |
|   |   |   | Enterprise Domain Entities (Pure)     |   |   | |
|   |   |   +---------------------------------------+   |   | |
|   |   +-----------------------------------------------+   | |
|   +-------------------------------------------------------+ |
+-------------------------------------------------------------+
```

---

## 2. Layer-by-Layer Architectural Breakdown

### Layer 1: Enterprise Domain Entities (Innermost Core)
- **Role**: Encapsulates enterprise-wide business models, value objects, and domain invariants.
- **Rules**: Zero external imports. Does not reference database ORMs (e.g. no SQLAlchemy base, no Prisma models) or HTTP serializers.
- **Example**: Pure Pydantic v2 domain models or Python dataclasses enforcing state transitions (e.g., `Order`, `ConsultationSession`, `PaymentRecord`).

### Layer 2: Application Use Cases & Domain Services
- **Role**: Encapsulates application-specific workflows, business transaction boundaries, and orchestration logic.
- **Contract**: Every Functional Requirement (FR) directly maps to an atomic Use Case (e.g., `CreateOrderUseCase`, `AuthorizeConsultationUseCase`).
- **Ports (Abstract Interfaces)**: Declares abstract repository interfaces (e.g., `UserRepositoryInterface`, `NotificationGatewayInterface`). It defines *what* data is needed, never *how* it is persisted.

### Layer 3: Interface Adapters (Ports & Adapters)
- **Role**: Translates data between use-case domain structures and delivery-specific schemas.
- **Controllers & API Routers**: FastAPI APIRouter handlers, REST controllers, and GraphQL resolvers.
- **Gateways & Repositories**: Implements the abstract repository ports defined in Layer 2 (e.g., `SQLAlchemyUserRepository` implements `UserRepositoryInterface`).
- **Data Transfer Objects (DTOs)**: Request and response validation contracts, mapping wire JSON to domain entities.

### Layer 4: Frameworks, Drivers & Infrastructure (Outermost Tier)
- **Role**: Contains concrete technical components, third-party libraries, and deployable infrastructure.
- **Components**: PostgreSQL database engines, Redis caching drivers, Qdrant vector storage clients, HTTP clients (httpx), background task queues (Celery/ARQ), and Docker runtime configurations.

---

## 3. Recommended Technology Stack Mappings

| Role | Primary Technology | Recommended Library / Tool | Architectural Justification |
| :--- | :--- | :--- | :--- |
| **API Framework** | Python 3.11+ / FastAPI | Starlette, Pydantic v2 | High asynchronous throughput, native OpenAPI 3.0 generation, automated schema validation |
| **Data Persistence** | PostgreSQL 16+ | SQLAlchemy 2.0 (Async), Alembic | ACID transactional guarantees, strong relational foreign-key integrity, JSONB semi-structured storage |
| **Caching & Queueing**| Redis 7+ | redis-py, aioredis | Sub-millisecond in-memory key-value latency, atomic counters, pub/sub signaling |
| **Domain Modeling** | Pydantic v2 / Pure Python | Dataclasses, Type Hints | Zero-overhead type safety, strict domain invariant verification, fast C-core serialization |
| **Testing Suite** | Pytest | pytest-asyncio, httpx.TestClient | 100% unit-testability of use cases using in-memory mock repositories without network access |

---

## 4. Decision Framework: When to Select Clean Architecture

### Recommended Scenarios:
1. **High Domain Complexity**: Systems with complex business logic, strict audit requirements, or multi-step validation workflows.
2. **Long Lifecycle & Evolution**: Applications expected to evolve over 3+ years where database drivers or web frameworks may be swapped.
3. **Traceability Requirements**: Regulated environments (healthcare, fintech, defense) requiring 1:1 mathematical traceability between IEEE 830 functional requirements and implementation modules.

### Anti-Patterns & When to Avoid:
- **Simple CRUD Applications**: If the application merely reads and writes directly from a database without domain logic, Clean Architecture introduces unnecessary repository abstraction overhead.
- **Strict Latency Ultra-Micro-Benchmarks**: Ultra-high-frequency trading systems where function-call callstack depth must be minimized.

---

## 5. Architectural Trade-offs Matrix

| Quality Attribute | Rating | Technical Trade-off Explanation | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Testability** | High (5/5) | Complete decoupling allows 100% unit testing of business rules via in-memory mock repositories. | Use dependency injection container or factory functions. |
| **Maintainability** | High (5/5) | UI and database changes have zero ripple effect on core domain algorithms. | Enforce strict linter boundary checks (e.g. import-linter). |
| **Initial Velocity** | Medium (3/5) | Requires writing repository interfaces, DTO mappers, and domain entities before coding features. | Use standard modular scaffolding and generic repository templates. |
| **Callstack Overhead** | Low (4/5) | Layer transitions add negligible microseconds in Python 3.11+. | Keep mapper functions lean and vectorize bulk transformations. |
