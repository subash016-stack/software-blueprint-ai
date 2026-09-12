# End-to-End Multi-Tier Traceability Matrix

## 1. Traceability Architecture

Software Blueprint AI establishes an unbroken, multi-tier directed acyclic graph (DAG) across all synthesized engineering entities:

```
[Stakeholders] (ST-001..n)
       │
       ▼
[Requirements] (FR-001..n, NFR-001..n)
       │
       ▼
[Project Modules] (MOD-001..n)
       │
       ▼
[Architecture Components] (COMP-001..n)
       │
       ▼
[APIs & Databases] (API-001..n, DB-001..n)
       │
       ▼
[WBS Tasks] (T-001..n)
       │
       ▼
[Milestones] (M-001..n)
```

---

## 2. Graph Construction with NetworkX

Traceability is modeled programmatically via Python `NetworkX` in `app/services/graph_service.py`.

### Node Types & ID Conventions:
- **`stakeholder`**: `ST-001`
- **`requirement`**: `FR-001`, `NFR-001`
- **`module`**: `MOD-001`
- **`component`**: `COMP-001`
- **`api`**: `API-001`
- **`database`**: `DB-001`
- **`task`**: `T-001`
- **`milestone`**: `M-001`

### Edge Semantics:
- `(ST, FR)`: `requires`
- `(FR, MOD)`: `allocated_to`
- `(MOD, COMP)`: `composed_of`
- `(COMP, API)`: `exposes`
- `(COMP, DB)`: `persists_in`
- `(FR, T)`: `implemented_by`
- `(T, M)`: `delivers`
- `(T_i, T_j)`: `depends_on`

---

## 3. Orphan Detection & Deterministic Scoring

The validation engine runs graph traversal audits to flag:
1. **Orphan Requirements**: Functional requirements not allocated to any task or module.
2. **Orphan Tasks**: Tasks with empty requirement references.
3. **Orphan Components**: Architectural components not mapped to any module or API.
4. **Missing Milestones**: Tasks left unallocated to delivery milestones.

Traceability coverage is calculated deterministically:
$$\text{Traceability Coverage} = \frac{\text{Mapped Entities}}{\text{Total Entities}} \times 100\%$$
