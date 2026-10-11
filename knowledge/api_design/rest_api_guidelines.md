# RESTful API Design, Versioning, and Protocol Guidelines

## Document Metadata
- **Document ID**: API-001
- **Category**: API Design
- **Authoritative Source**: Fielding, R. T. (2000). Architectural Styles and the Design of Network-based Software Architectures; RFC 7807 (Problem Details for HTTP APIs); OpenAPI 3.0.3 Specification.
- **Target Systems**: Public APIs, Mobile Backend-as-a-Service, Internal Microservice Endpoints, Partner Integrations

---

## 1. Core Architectural Foundation: Richardson Maturity Model

Modern enterprise API design adheres to the **Richardson Maturity Model**:
- **Level 0 (The Swamp of POX)**: Single URI, single HTTP verb (usually POST), tunneling commands (e.g. SOAP or naive RPC).
- **Level 1 (Resources)**: Dedicated resource URIs for different entities (e.g. `/orders`, `/users`).
- **Level 2 (HTTP Verbs & Status Codes)**: Correct use of standard HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) and precise RFC status codes.
- **Level 3 (Hypermedia Controls / HATEOAS)**: Responses embed navigational links (`_links`) informing clients of valid subsequent state transitions.

*Target Standard for Software Blueprint AI*: **Level 2+ with strict schema contracts, OpenAPI 3.0 documentation, and predictable URI structures.**

---

## 2. Resource Naming & URI Path Conventions

1. **Nouns, Not Verbs**: URIs identify resources, not remote procedure actions.
   - ✅ Correct: `POST /api/v1/orders` (Create order)
   - ❌ Incorrect: `POST /api/v1/createOrder`
2. **Plural Resource Collections**: Use lowercase, plural nouns.
   - ✅ Correct: `/api/v1/users`, `/api/v1/telemetry-readings`
3. **Hierarchical Relationships**:
   - `/api/v1/users/{user_id}/consultations` (Consultations belonging to a specific user)
   - Keep nesting shallow ($\le 2$ levels). For deeper queries, use top-level resources with query filters:
     - `/api/v1/prescriptions?consultation_id={id}`
4. **API Versioning Strategy**:
   - Standard: **URI Path Versioning** (`/api/v1/...`). Guarantees explicit caching, predictable routing in reverse proxies (Nginx/Traefik), and unambiguous documentation.

---

## 3. HTTP Verb Semantics & Idempotency Rules

| HTTP Method | Action | RFC Idempotent | RFC Safe | Expected Success Status | Body in Request | Body in Response |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **GET** | Retrieve resource or collection | ✅ Yes | ✅ Yes | `200 OK` | ❌ No | ✅ Resource JSON |
| **POST** | Create resource or initiate operation | ❌ No | ❌ No | `201 Created` / `202 Accepted` | ✅ Request Payload | ✅ Created Resource |
| **PUT** | Complete resource replacement | ✅ Yes | ❌ No | `200 OK` / `204 No Content` | ✅ Full Resource | ✅ Updated Resource |
| **PATCH** | Partial resource mutation | ❌ No | ❌ No | `200 OK` | ✅ Delta Fields | ✅ Updated Resource |
| **DELETE** | Remove resource | ✅ Yes | ❌ No | `204 No Content` / `200 OK` | ❌ No | ❌ Empty (or confirmation) |

### The `Idempotency-Key` Pattern for Mutable POSTs:
For payment processing, order dispatch, or financial credits, clients send a unique `Idempotency-Key: <UUID>` header. The API Gateway or FastAPI middleware atomically caches the response in Redis for 24 hours. Repeating the same request returns the cached result without re-executing business transactions.

---

## 4. Standardized Error Contract: RFC 7807 (Problem Details)

Every 4xx and 5xx error response MUST return a standardized JSON structure conforming to **RFC 7807**:

```json
{
  "type": "https://api.softwareblueprint.ai/errors/invalid-entity",
  "title": "Validation Failed",
  "status": 422,
  "detail": "Field 'consultation_time' must be in future ISO-8601 format.",
  "instance": "/api/v1/consultations",
  "invalid_params": [
    {"field": "consultation_time", "reason": "Timestamp has already passed"}
  ]
}
```

---

## 5. Protocol Selection Decision Matrix: REST vs. gRPC vs. GraphQL vs. WebSockets

| Protocol | Best Used For | Serialization Format | Network Transport | Trade-offs & Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **REST (HTTP/JSON)** | Public APIs, Web Frontends, CRUD Services | Human-readable JSON | HTTP/1.1 or HTTP/2 | Higher bandwidth overhead; over-fetching/under-fetching data |
| **gRPC** | Internal high-throughput Microservice-to-Microservice calls | Binary Protocol Buffers (Protobuf) | HTTP/2 Multiplexing | Requires generated client stubs; difficult for direct browser JS calls without gRPC-Web proxy |
| **GraphQL** | Multi-screen client apps (Mobile + Web) with heterogeneous data needs | JSON | HTTP/1.1 POST | Complex caching at CDN layer; risk of expensive recursive client queries |
| **WebSockets** | Real-time bidirectional telemetry, chat, collaborative editing, live auction boards | Text / Binary Frames | RFC 6455 persistent TCP socket | Stateful connections require sticky load balancing and Redis adapter backplanes |

---

## 6. Pagination, Filtering & Rate Limiting

- **Pagination Pattern**: Cursor-based pagination (`?cursor=eyJpZCI...&limit=50`) is preferred over offset/limit (`?offset=1000`) for large datasets, avoiding query degradation and duplicate records during concurrent insertions.
- **Rate Limiting**:
  - Algorithm: **Redis Sliding Window Counter** (`ZADD` + `ZREMRANGEBYSCORE`).
  - Response Headers:
    - `X-RateLimit-Limit: 1000`
    - `X-RateLimit-Remaining: 842`
    - `X-RateLimit-Reset: 1718042400`
    - Status code on breach: `429 Too Many Requests`
