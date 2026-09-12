# Enterprise Security: OAuth2, JWT, and Role-Based Access Control

## Document Metadata
- **Document ID**: SEC-001
- **Category**: Security Architecture
- **Section**: Authentication & Authorization Best Practices
- **Authoritative Source**: RFC 6749 (The OAuth 2.0 Authorization Framework) & OWASP API Security Top 10.

## Core Architecture
1. **Stateless Authentication**: Implement asymmetric RSA/ECDSA signed JSON Web Tokens (JWT) for access tokens with short TTLs (15 minutes) paired with cryptographically secure, rotatable Refresh Tokens stored in Redis.
2. **Role-Based Access Control (RBAC)**: Fine-grained scopes and roles mapped to endpoints (`read:orders`, `write:orders`, `admin:all`).
3. **Password Security**: Argon2id or Bcrypt hashing with high work factors and per-user cryptographic salts.
4. **Transport Security & Zero Trust**: Strict TLS 1.3 encryption, CORS whitelist validation, parameterized SQL queries preventing SQL injection, and rate limiting against credential stuffing.
