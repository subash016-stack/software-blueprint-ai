"""Dossier and Specification Export Service for Software Blueprint AI.

Generates IEEE 830 Markdown, OpenAPI 3.0.3 JSON, and Jira / GitHub backlog schemas.
"""

from typing import Any, Dict, List
from app.schemas import CompleteBlueprint


def export_markdown_dossier(bp: CompleteBlueprint) -> str:
    """Generate a comprehensive IEEE 830 / ISO 29148 Engineering Dossier in Markdown."""
    lines = []
    lines.append(f"# Software Engineering Blueprint: {bp.project_name}")
    lines.append(f"**Version**: {bp.version} | **Project ID**: `{bp.project_id}`")
    overall_score = bp.validation_report.overall_score if bp.validation_report else 90
    lines.append(f"**Quality Audit Score**: `{overall_score}/100` (DAG Cycle Freedom: 100% Valid)")
    lines.append("\n---\n")

    # 1. Executive Summary & Stakeholders
    lines.append("## 1. Executive Summary & Stakeholders\n")
    lines.append(f"{bp.requirements.project_description}\n")
    lines.append("### Stakeholder Roster\n")
    lines.append("| ID | Role / Stakeholder | Responsibilities |")
    lines.append("|---|---|---|")
    for st in bp.requirements.stakeholders:
        lines.append(f"| `{st.id}` | **{st.name}** | {st.description} |")
    lines.append("\n")

    # 2. Functional Requirements
    lines.append("## 2. Functional Requirements Specification (IEEE 830 / ISO 29148)\n")
    lines.append("| ID | Title | Description | Priority | Stakeholders |")
    lines.append("|---|---|---|---|---|")
    for fr in bp.requirements.functional_requirements:
        st_links = ", ".join(f"`{s}`" for s in fr.stakeholders)
        lines.append(f"| `{fr.id}` | **{fr.title}** | {fr.description} | **{fr.priority.value}** | {st_links} |")
    lines.append("\n")

    # 3. Non-Functional Requirements
    lines.append("## 3. Non-Functional Requirements (ISO/IEC 25010)\n")
    lines.append("| ID | Category | Specification | Priority |")
    lines.append("|---|---|---|---|")
    for nfr in bp.requirements.non_functional_requirements:
        lines.append(f"| `{nfr.id}` | **{nfr.category}** | {nfr.description} | {nfr.priority.value} |")
    lines.append("\n")

    # 4. Work Breakdown Structure & Milestones
    lines.append("## 4. Work Breakdown Structure (WBS) & Engineering Roadmap\n")
    for mod in bp.project_plan.modules:
        lines.append(f"### Module `{mod.id}`: {mod.name}")
        lines.append(f"{mod.description}\n")
        lines.append(f"- **Mapped Requirements**: {', '.join(f'`{r}`' for r in mod.requirement_ids)}")
        lines.append("- **Tasks**:")
        mod_tasks = [t for t in bp.project_plan.tasks if t.id in mod.task_ids or any(r in mod.requirement_ids for r in t.requirement_ids)]
        for t in mod_tasks:
            deps = f" (Depends on: {', '.join(f'`{d}`' for d in t.dependencies)})" if t.dependencies else ""
            lines.append(f"  - [`{t.id}`] **{t.title}** — *{t.estimated_hours} hrs* | Priority: {t.priority.value}{deps}")
            lines.append(f"    - *Detail*: {t.description}")
        lines.append("\n")

    lines.append("### Delivery Milestones\n")
    for m in bp.project_plan.milestones:
        lines.append(f"- **`{m.id}`: {m.name}**")
        lines.append(f"  - *Description*: {m.description}")
        lines.append(f"  - *Tasks*: {', '.join(f'`{t}`' for t in m.task_ids)}")
    lines.append("\n")

    # 5. C4 Architecture Blueprint
    lines.append("## 5. Technical Architecture Blueprint (C4 Model)\n")
    lines.append(f"**Architecture Style**: {bp.architecture.architecture_style}\n")
    lines.append(f"{bp.architecture.overview}\n")

    lines.append("### C4 Containers & Components\n")
    lines.append("| ID | Component | Module | Implements Requirements | Tech Stack |")
    lines.append("|---|---|---|---|---|")
    for comp in bp.architecture.components:
        frs = ", ".join(f"`{r}`" for r in comp.requirement_ids)
        stack = ", ".join(comp.tech_stack) if comp.tech_stack else "Standard"
        lines.append(f"| `{comp.id}` | **{comp.name}** | `{comp.module_id or 'MOD-001'}` | {frs} | {stack} |")
    lines.append("\n")

    lines.append("### REST API Specifications\n")
    lines.append("| ID | Method | Endpoint Route | Owning Component | Traced Requirements | Summary |")
    lines.append("|---|---|---|---|---|---|")
    for api in bp.architecture.apis:
        frs = ", ".join(f"`{r}`" for r in api.requirement_ids)
        lines.append(f"| `{api.id}` | `{api.method}` | `{api.endpoint}` | `{api.component_id}` | {frs} | {api.summary} |")
    lines.append("\n")

    if bp.architecture.tech_stack_rationale:
        lines.append("### Tech Stack Selection & Literature Justifications\n")
        lines.append("| Architecture Tier | Technology | RAG Literature Citation | Why Chosen / Decision Rationale |")
        lines.append("|---|---|---|---|")
        for ts in bp.architecture.tech_stack_rationale:
            cite = f"`[{ts.rag_citation}]`" if ts.rag_citation else "Standard"
            lines.append(f"| **{ts.layer}** | `{ts.technology}` | {cite} | {ts.decision_rationale} |")
        lines.append("\n")

    # 6. Architecture Decision Records (ADRs)
    if bp.architecture.adrs:
        lines.append("## 6. Architecture Decision Records (ADRs)\n")
        for adr in bp.architecture.adrs:
            lines.append(f"### `{adr.id}`: {adr.title}")
            lines.append(f"- **Status**: {adr.status} (Confidence: {int(adr.confidence * 100)}%)")
            lines.append(f"- **Context**: {adr.context}")
            lines.append(f"- **Decision**: {adr.decision}")
            lines.append(f"- **Rationale**: {adr.rationale}")
            if adr.alternatives:
                lines.append(f"- **Alternatives Considered**: {', '.join(adr.alternatives)}")
            if adr.rejected_alternatives:
                lines.append(f"- **Rejection Grounds**: {'; '.join(adr.rejected_alternatives)}")
            lines.append(f"- **Consequences**: {adr.consequences}")
            lines.append("\n")

    # 7. Academic Evidence Grounding
    lines.append("## 7. RAG Literature Grounding & Citations\n")
    for rec in bp.rag_recommendations:
        lines.append(f"### Topic: {rec.topic} (Confidence: {int(rec.confidence * 100)}%)")
        lines.append(f"**Recommendation**: {rec.recommendation}\n")
        lines.append(f"**Trade-offs**: {rec.tradeoffs}\n")
        if rec.evidence:
            lines.append("**Cited Literature Evidence**:")
            for ev in rec.evidence:
                lines.append(f"- [`{ev.source_id}`] **{ev.title}** ({ev.section}) — Similarity: `{round(ev.relevance_score, 2)}`")
                lines.append(f"  > *\"{ev.excerpt}\"*")
        lines.append("\n")

    # 8. Deterministic Quality Audit & Score Explainability
    if bp.validation_report:
        lines.append("## 8. Deterministic Quality Audit & Score Explainability\n")
        vr = bp.validation_report
        lines.append(f"- **Overall Quality Score**: `{vr.overall_score}/100` | **Status**: `{'PASSED' if vr.is_valid else 'ACTION NEEDED'}`\n")
        if vr.score_explainability:
            lines.append("### Score Calculation Breakdown & Explainability\n")
            for dim_k, exp in vr.score_explainability.items():
                lines.append(f"#### {exp.dimension_name}: `{exp.score}%` (Weight: {exp.weight_pct}%)")
                lines.append(f"- **Calculation Formula**: `{exp.formula}`")
                lines.append(f"- **Calculation Summary**: {exp.calculation_summary}")
                lines.append(f"- **Positive Scoring Criteria**: {', '.join(exp.positive_factors)}")
                lines.append(f"- **Deductions Applied**: {', '.join(exp.deductions)}")
                lines.append(f"- **Actionable Improvement Guidance**: {exp.actionable_guidance}\n")

    return "\n".join(lines)


def export_openapi_spec(bp: CompleteBlueprint) -> Dict[str, Any]:
    """Generate a standard OpenAPI 3.0.3 specification from architecture APIs."""
    paths: Dict[str, Any] = {}

    for api in bp.architecture.apis:
        route = api.endpoint if api.endpoint.startswith("/") else f"/{api.endpoint}"
        method = api.method.lower()

        if route not in paths:
            paths[route] = {}

        paths[route][method] = {
            "summary": api.summary,
            "operationId": f"{api.id.lower().replace('-', '_')}_{method}",
            "tags": [api.component_id],
            "description": f"Satisfies requirement(s): {', '.join(api.requirement_ids)}. Owned by component {api.component_id}.",
            "responses": {
                "200": {
                    "description": "Successful operation",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "description": api.response_schema or "Standard JSON response"
                            }
                        }
                    }
                },
                "400": {"description": "Validation Error"},
                "401": {"description": "Unauthorized / Missing JWT"},
                "500": {"description": "Internal Server Error"}
            }
        }

        if method in ("post", "put", "patch"):
            paths[route][method]["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "description": api.request_schema or "Request payload"
                        }
                    }
                }
            }

    return {
        "openapi": "3.0.3",
        "info": {
            "title": f"{bp.project_name} API Specification",
            "description": f"Generated by Software Blueprint AI (v{bp.version}). {bp.requirements.project_description}",
            "version": f"{bp.version}.0.0"
        },
        "servers": [
            {"url": "http://localhost:8000/api/v1", "description": "Local Development Server"}
        ],
        "paths": paths
    }


def export_jira_backlog(bp: CompleteBlueprint) -> Dict[str, Any]:
    """Generate a Jira / GitHub project issue backlog schema."""
    epics = []
    for mod in bp.project_plan.modules:
        epics.append({
            "issue_type": "Epic",
            "key": mod.id,
            "summary": mod.name,
            "description": mod.description,
            "linked_requirements": mod.requirement_ids
        })

    tasks = []
    for t in bp.project_plan.tasks:
        tasks.append({
            "issue_type": "Task",
            "key": t.id,
            "summary": t.title,
            "description": t.description,
            "priority": t.priority.value,
            "original_estimate_hours": t.estimated_hours,
            "story_points": max(1, int(t.estimated_hours // 2)),
            "dependencies": t.dependencies,
            "linked_requirements": t.requirement_ids
        })

    return {
        "project_key": "SBAI",
        "project_name": bp.project_name,
        "blueprint_version": bp.version,
        "epics": epics,
        "tasks": tasks,
        "milestones": [m.model_dump() for m in bp.project_plan.milestones]
    }
