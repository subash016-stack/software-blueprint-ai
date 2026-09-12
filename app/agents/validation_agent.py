"""Module 5: Validation & Quality Scoring Agent.

Executes deterministic structural/traceability audits and semantic consistency checks
to generate a multi-dimensional Software Engineering Blueprint Quality Score.
"""

import logging
from typing import List
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

from app.schemas import (
    RequirementAnalysis,
    ProjectPlan,
    ArchitectureBlueprint,
    ValidationReport
)
from app.state import BlueprintState
from app.validation.deterministic import run_deterministic_audit
from app.llm.factory import invoke_structured
from app.cache.redis_client import cache_manager
from app.config import get_settings

logger = logging.getLogger("software-blueprint-ai.validation")

VALIDATION_SYSTEM_PROMPT = """You are a Senior Software Quality Assurance Architect and Engineering Auditor.

Review the deterministic audit findings, requirement specification, and architecture blueprint to generate high-value engineering recommendations.

Focus on:
1. Security and data protection gaps.
2. High-availability and failure recovery considerations.
3. Architecture maintainability and long-term testability recommendations.

Return concise, actionable recommendations conforming strictly to the requested JSON schema.
"""


def validate_blueprint(
    requirements: RequirementAnalysis,
    project_plan: ProjectPlan,
    architecture: ArchitectureBlueprint,
    run_llm_recommendations: bool = False
) -> ValidationReport:
    """Perform deterministic checks, compute quality scores, and synthesize recommendations."""
    settings = get_settings()

    # 1. Deterministic Python Audit (DAG cycles, broken links, coverage, score)
    critical_issues, warnings, scores = run_deterministic_audit(
        requirements,
        project_plan,
        architecture
    )

    recommendations = [
        "Implement end-to-end integration tests for all high-priority (Must) requirements.",
        "Enforce rate-limiting and JWT token expiry validation across public endpoints.",
        "Ensure database connection pooling and asynchronous query execution are configured for scale."
    ]

    if run_llm_recommendations:
        cache_input = {
            "req_hash": requirements.compute_hash(),
            "arch_hash": architecture.compute_hash(),
            "issues_count": len(critical_issues) + len(warnings)
        }
        cache_key = cache_manager.build_cache_key(
            operation="validation_recommendations",
            input_data=cache_input,
            prompt_version=settings.validation_prompt_version,
            schema_version=settings.schema_version
        )
        cached_recs = cache_manager.get(cache_key)

        if cached_recs and isinstance(cached_recs, list):
            recommendations = cached_recs
        else:
            prompt_content = f"""Review this software system audit:
Project: {requirements.project_name}
Critical Issues: {[i.model_dump() for i in critical_issues]}
Warnings: {[w.model_dump() for w in warnings]}
Traceability Score: {scores.traceability_coverage}%

Provide 3 concise, actionable architectural recommendations to maximize engineering robustness:
{{
  "recommendations": [
    "Ensure automated integration tests validate end-to-end API payloads against Pydantic contracts.",
    "Implement distributed tracing with OpenTelemetry across backend services.",
    "Configure Redis rate limiting on public authentication endpoints to mitigate brute-force attacks."
  ]
}}
"""

            class RecsResponse(BaseModel):
                recommendations: List[str]

            messages = [
                SystemMessage(content=VALIDATION_SYSTEM_PROMPT),
                HumanMessage(content=prompt_content),
            ]

            try:
                res = invoke_structured(messages, RecsResponse)
                recommendations = res.recommendations
                cache_manager.set(cache_key, recommendations)
            except Exception as e:
                logger.warning("Validation LLM call failed (%s). Using standard best practice recommendations.", e)

    is_valid = len(critical_issues) == 0

    return ValidationReport(
        is_valid=is_valid,
        overall_score=scores.overall_score,
        score_breakdown=scores,
        critical_issues=critical_issues,
        warnings=warnings,
        recommendations=recommendations
    )


def validation_agent_node(state: BlueprintState) -> BlueprintState:
    """LangGraph node for Module 5: Validation Agent."""
    requirements = state.get("requirements")
    project_plan = state.get("project_plan")
    architecture = state.get("architecture")

    if not requirements or not project_plan or not architecture:
        errors = list(state.get("errors", []))
        errors.append("ValidationAgent error: Incomplete upstream state (missing SRS, plan, or architecture).")
        return {**state, "errors": errors}

    try:
        report = validate_blueprint(requirements, project_plan, architecture)
        return {
            **state,
            "validation_report": report
        }
    except Exception as e:
        logger.error("ValidationAgent execution failed: %s", e)
        errors = list(state.get("errors", []))
        errors.append(f"ValidationAgent error: {str(e)}")
        return {**state, "errors": errors}
