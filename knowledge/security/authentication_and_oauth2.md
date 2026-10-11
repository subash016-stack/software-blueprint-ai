# Enterprise Security: OAuth 2.1, JWT, and Zero-Trust Access Control

## Document Metadata
- **Document ID**: SEC-001
- **Category**: Security Architecture & Identity
- **Authoritative Source**: RFC 6749 (The OAuth 2.0 Authorization Framework); RFC 9068 (JWT Profile for OAuth 2.0 Access Tokens); OAuth 2.1 Draft Spec; OWASP API Security Top 10 (2023).
- **Target Systems**: Multi-tenant SaaS, REST/GraphQL APIs, Microservices Gateways, Enterprise Web & Mobile Clients.

---

## 1. Authentication Standards & Protocols

Modern enterprise systems must avoid deprecated authorization flows (such as OAuth 2.0 Implicit Grant and Resource Owner Password Credentials Grant).

### 1.1 OAuth 2.1 and OpenID Connect (OIDC) Core Architecture
- **Authorization Code Grant with PKCE (Proof Key for Code Exchange)**:
  - Required for all clients (Single Page Applications, Native Mobile Apps, and Server-Side Web Apps).
  - Client generates a cryptographically random `code_verifier` and computes `code_challenge = BASE64URL(SHA256(code_verifier))`.
  - Protects against authorization code interception attacks without requiring client secrets on public devices.
- **OIDC Identity Layer**:
  - Delivers identity claims via standard signed `id_token` (JWT format containing `sub`, `email`, `aud`, `iss`).
  - Separation of Concerns: `id_token` is for user authentication on the client; opaque or signed `access_token` is for authorizing API resource requests.

### 1.2 Cryptographic Token Design: Asymmetric JWT vs. Opaque Tokens
- **Asymmetric Signature (RS256 / Ed25519)**:
  - Authentication Server signs Access Tokens using a private cryptographic key.
  - Resource Servers (Microservices / APIs) verify signatures autonomously using the public key fetched from the Identity Provider's `jwks_uri` (`/.well-known/jwks.json`).
  - Eliminates synchronous database roundtrips on every API call.
- **Token Lifespans & Storage**:
  - **Access Token TTL**: 10 to 15 minutes max.
  - **Refresh Token Rotation (RTR)**: Refresh tokens are single-use. Every refresh exchanges the current token for a new access token and a brand-new refresh token. If a previously consumed refresh token is presented, the auth server invalidates all child sessions (token theft detection).
  - **Browser Storage**: Store access tokens in memory; store refresh tokens in an `HttpOnly`, `Secure`, `SameSite=Strict` cookie to eliminate Cross-Site Scripting (XSS) extraction risks.

---

## 2. Authorization Models: RBAC vs. ABAC

### 2.1 Role-Based Access Control (RBAC)
- Users are assigned roles (e.g., `Viewer`, `Editor`, `WorkspaceAdmin`, `SuperAdmin`).
- Roles map directly to operational scopes:
  - `blueprints:read`
  - `blueprints:write`
  - `blueprints:delete`
  - `billing:admin`
- Evaluated at API Gateway or Controller middleware level via declarative annotations (e.g., `@require_scope("blueprints:write")`).

### 2.2 Attribute-Based Access Control (ABAC) / Fine-Grained Policy
- When role alone is insufficient (e.g., "A user can edit a Blueprint ONLY IF they are the creator AND the workspace status is active"):
- Implement policy engines such as **Open Policy Agent (OPA)** or **Cedar Policy**.
- Evaluates context tuples: `{subject, action, resource, environment}`.

---

## 3. Password Hashing & Secret Cryptography
- **Password Hashes**: Utilize **Argon2id** (memory-hard, resistant to GPU/ASIC cracking) with minimum params: `t=3 iterations`, `m=64MB memory`, `p=4 parallelism`. Fallback to **Bcrypt** with minimum work factor `12`.
- **API Keys**: Hash stored API keys using **SHA-256** with unique salts. Never store plaintext API keys in the database. Provide key prefixes (e.g., `sbp_live_...`) to enable automated secret scanning in Git repositories.

---

## 4. API Hardening & OWASP Compliance

1. **RFC 7807 Security Errors**: Never leak stack traces, database schemas, or internal server errors to clients.
2. **CORS (Cross-Origin Resource Sharing)**: Explicitly restrict origins (`Access-Control-Allow-Origin: https://app.example.com`). Avoid wildcard `*` with credentials.
3. **Rate Limiting & Anti-Brute-Force**: Enforce Redis Token Bucket rate limiting:
   - Login endpoints: Max 5 attempts per minute per IP.
   - Resource endpoints: Max 100 requests per minute per authenticated user.
4. **Content Security Policy (CSP)**: `default-src 'self'; script-src 'self'; frame-ancestors 'none';`.

---

## 5. Decision Rules for Architecture Agent
- When designing modern web or microservices platforms, specify **OAuth 2.1 with PKCE** and **RS256 JWT** authentication.
- For backend-to-backend internal microservice communication, specify **Mutual TLS (mTLS)** or service-to-service signed JWT bearer tokens.
- Generate an Architectural Decision Record (ADR) citing `SEC-001` for **Stateless Asymmetric JWT with Refresh Token Rotation**.
