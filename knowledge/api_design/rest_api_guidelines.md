# RESTful API Design, Versioning, and Idempotency

## Document Metadata
- **Document ID**: API-001
- **Category**: API Design
- **Section**: REST Best Practices & Idempotent Mutators
- **Authoritative Source**: Fielding, R. T. (2000). Architectural Styles and the Design of Network-based Software Architectures.

## Core Principles
1. **Resource-Oriented URIs**: Endpoints represent domain nouns rather than verbs (e.g. `/api/v1/orders`, `/api/v1/users/{id}/orders`).
2. **Idempotency**: All `GET`, `PUT`, `DELETE`, and `HEAD` requests must be strictly idempotent. For mutable `POST` operations (such as payment processing), an `Idempotency-Key` header with Redis cache validation prevents duplicate transaction execution.
3. **HTTP Status Semantics**: Use standard RFC status codes: `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`, `429 Too Many Requests`, and `500 Internal Server Error`.
4. **Rate Limiting**: Protect backend endpoints using sliding window token bucket rate limiters in Redis.
