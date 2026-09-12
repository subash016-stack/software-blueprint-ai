# Module 6: Requirement Change Impact Analysis & Targeted Selective Regeneration

## 1. Research Motivation

In traditional AI code generation workflows, any change to a requirement triggers complete regeneration of the entire specification. This causes:
- High token wastage ($100\%$ re-synthesis cost)
- Non-deterministic drift in unrelated components
- Severe GPU/CPU latency spikes

Software Blueprint AI introduces **Targeted Selective Regeneration**, leveraging the multi-tier traceability DAG to isolate the exact downstream blast radius and regenerate **only** affected nodes, producing **Blueprint v2**.

```
                       Modified Requirement (e.g. FR-001)
                                      │
                                      ▼
                        [NetworkX Blast Radius Traversal]
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼                                                   ▼
   [Affected Downstream Nodes]                         [Unaffected Stable Nodes]
   • Affected Tasks: {T-001, T-002}                    • Tasks: {T-003, T-004, T-005}
   • Affected Components: {COMP-001}                   • Components: {COMP-002, COMP-003}
   • Affected APIs: {API-001}                          • APIs: {API-002, API-003}
   • Affected Milestones: {M-001}                      • Milestones: {M-002, M-003}
            │                                                   │
            ▼                                                   ▼
  [Targeted LLM / Graph Synthesis]                     [Preserved Intact (Cached)]
            │                                                   │
            └─────────────────────────┬─────────────────────────┘
                                      ▼
                       [Re-assembled Blueprint v2]
                      • ~78% Measured Token Savings
                      • Full Change Audit & Diff
```

---

## 2. Blast Radius Algorithm

1. Find target requirement node $n_{\text{req}}$ in directed graph $G$.
2. Traverse all forward reachable descendants using DFS/BFS:
   $$\text{BlastRadius}(n_{\text{req}}) = \left\{ v \in V(G) \mid \exists \text{ path } n_{\text{req}} \leadsto v \right\}$$
3. Categorize affected nodes by entity type (`tasks`, `components`, `apis`, `databases`, `milestones`).
4. Calculate additional and modified effort $\Delta \text{Hours}$.

---

## 3. Versioning & Immutability

When applying targeted selective regeneration:
- A new immutable snapshot is appended to `version_history`.
- `version` is bumped ($1 \rightarrow 2$).
- Change log records `modified_requirements`, `regenerated_tasks`, `regenerated_components`, and `token_savings_percent`.
