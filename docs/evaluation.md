# Evaluation & Benchmarking Framework

## 1. Experimental Methodology

Software Blueprint AI provides a reproducible benchmark suite (`scripts/evaluate.py`) that evaluates the multi-agent pipeline across 5 comparative configurations:

- **Exp A**: Monolithic Single LLM Prompt (Baseline)
- **Exp B**: LLM with Strict Pydantic Output Formatting
- **Exp C**: Decoupled Multi-Agent Pipeline (Requirements + Planning + Architecture)
- **Exp D**: Multi-Agent Pipeline with Academic RAG Grounding
- **Exp E (Full Proposed System)**: Multi-Agent + RAG + Traceability DAG + Deterministic Validation + Targeted Impact Analysis

---

## 2. Evaluation Metrics

| Metric | Definition | Target Threshold |
|---|---|---|
| **DAG Cycle Freedom** | $\frac{\text{Valid Acyclic Graphs}}{\text{Total Runs}} \times 100\%$ | $100\%$ |
| **Traceability Coverage** | $\frac{\text{Mapped Requirement-Task-Component Links}}{\text{Total Expected Links}} \times 100\%$ | $\ge 95\%$ |
| **RAG Cosine Grounding** | Mean cosine similarity of cited architectural evidence chunks | $\ge 0.65$ |
| **Targeted Token Reduction** | $\frac{\text{Baseline Tokens} - \text{Regeneration Tokens}}{\text{Baseline Tokens}} \times 100\%$ | $\ge 70\%$ |
| **Deterministic Validation Score** | 7-factor composite quality metric ($0 \dots 100$) | $\ge 85 / 100$ |

---

## 3. Running the Benchmark

```powershell
.venv\Scripts\python.exe scripts/evaluate.py
```

Results are computed and output to terminal with full CSV/JSON export capability.
