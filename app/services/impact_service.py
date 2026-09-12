"""Requirement Change Impact Analysis and Targeted Selective Regeneration Service."""

import logging
from typing import List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

from app.schemas import (
    CompleteBlueprint,
    RequirementAnalysis,
    ProjectPlan,
    ArchitectureBlueprint,
    Task,
    ArchitectureComponent,
    ArchitectureAPI,
    ImpactReport,
    RequirementChangeRequest,
    BlueprintVersionSummary
)
from app.services.graph_service import traceability_service
from app.agents.validation_agent import validate_blueprint
from app.llm.factory import invoke_structured
from app.config import get_settings

logger = logging.getLogger("software-blueprint-ai.impact")

IMPACT_EXPLANATION_PROMPT = """You are a Principal Systems Analyst and Release Architect.

Analyze the downstream blast radius resulting from a requirement modification.
Given:
- Changed Requirement: {changed_fr}
- New Requirement Specification: {new_description}
- Affected Modules: {affected_modules}
- Affected Tasks: {affected_tasks}
- Affected Components: {affected_components}
- Affected APIs: {affected_apis}
- Affected Milestones: {affected_milestones}

Provide:
1. A concise, professional technical explanation of the downstream architectural and project impact.
2. 3 concrete recommended re-engineering actions.

Return JSON conforming strictly to the requested schema.
"""


class ImpactExplanationResponse(BaseModel):
    explanation: str
    recommended_actions: List[str]


def analyze_requirement_impact(
    blueprint: CompleteBlueprint,
    change_request: RequirementChangeRequest,
    generate_llm_explanation: bool = True
) -> ImpactReport:
    """Analyze downstream blast radius for a modified requirement using NetworkX."""
    # 1. Build current traceability graph
    traceability_service.build_graph(
        blueprint.requirements,
        blueprint.project_plan,
        blueprint.architecture
    )

    # 2. Compute deterministic downstream impact
    impact_data = traceability_service.analyze_downstream_impact(change_request.requirement_id)

    # 3. Find old requirement
    old_fr = next(
        (fr for fr in blueprint.requirements.functional_requirements if fr.id == change_request.requirement_id),
        None
    )
    old_fr_desc = old_fr.description if old_fr else "Requirement"

    explanation = (
        f"Modifying {change_request.requirement_id} directly propagates downstream changes across "
        f"{len(impact_data['affected_modules'])} module(s), {len(impact_data['affected_tasks'])} task(s), "
        f"and {len(impact_data['affected_components'])} architecture component(s) with an estimated effort delta of "
        f"+{impact_data['effort_hours_delta']} hours."
    )
    recommended_actions = [
        f"Refactor downstream task implementations ({', '.join(impact_data['affected_tasks']) or 'N/A'}).",
        f"Update API payloads for affected endpoints ({', '.join(impact_data['affected_apis']) or 'N/A'}).",
        "Re-run validation suite and regression tests."
    ]

    # 4. Generate LLM explanation if requested
    if generate_llm_explanation:
        prompt = IMPACT_EXPLANATION_PROMPT.format(
            changed_fr=f"{change_request.requirement_id}: {old_fr_desc}",
            new_description=change_request.new_description,
            affected_modules=impact_data["affected_modules"],
            affected_tasks=impact_data["affected_tasks"],
            affected_components=impact_data["affected_components"],
            affected_apis=impact_data["affected_apis"],
            affected_milestones=impact_data["affected_milestones"],
        )
        try:
            explanation_res = invoke_structured(
                [HumanMessage(content=prompt)],
                ImpactExplanationResponse
            )
            explanation = explanation_res.explanation
            recommended_actions = explanation_res.recommended_actions
        except Exception as e:
            logger.warning("Impact LLM explanation failed (%s). Using fallback summary.", e)

    return ImpactReport(
        changed_requirement_id=change_request.requirement_id,
        change_type="MODIFIED",
        impact_level=impact_data["impact_level"],
        affected_requirements=impact_data["affected_requirements"],
        affected_modules=impact_data["affected_modules"],
        affected_tasks=impact_data["affected_tasks"],
        affected_components=impact_data["affected_components"],
        affected_apis=impact_data["affected_apis"],
        affected_milestones=impact_data["affected_milestones"],
        effort_hours_delta=impact_data["effort_hours_delta"],
        explanation=explanation,
        recommended_actions=recommended_actions
    )


def apply_targeted_regeneration(
    blueprint: CompleteBlueprint,
    change_request: RequirementChangeRequest,
    impact_report: ImpactReport
) -> CompleteBlueprint:
    """Selectively regenerate ONLY affected tasks and architecture components to produce Blueprint v2."""
    logger.info("Executing Targeted Selective Regeneration for %s (v%d -> v%d)", 
                change_request.requirement_id, blueprint.version, blueprint.version + 1)

    # 1. Update the target requirement in SRS
    updated_reqs = blueprint.requirements.model_copy(deep=True)
    target_fr = next((fr for fr in updated_reqs.functional_requirements if fr.id == change_request.requirement_id), None)
    if target_fr:
        if change_request.new_title:
            target_fr.title = change_request.new_title
        target_fr.description = change_request.new_description
        if change_request.new_priority:
            target_fr.priority = change_request.new_priority

    # 2. Targeted Task Refinement (Preserve unaffected tasks, selectively adjust affected ones)
    updated_plan = blueprint.project_plan.model_copy(deep=True)
    affected_task_ids = set(impact_report.affected_tasks)

    for task in updated_plan.tasks:
        if task.id in affected_task_ids:
            # Append refinement note and update effort
            task.description = f"{task.description} [Refined for {change_request.requirement_id}: {change_request.new_description[:80]}...]"
            task.estimated_hours = round(task.estimated_hours * 1.25, 1)

    # 3. Targeted Architecture Refinement (Preserve unaffected components/APIs)
    updated_arch = blueprint.architecture.model_copy(deep=True)
    affected_comp_ids = set(impact_report.affected_components)

    for comp in updated_arch.components:
        if comp.id in affected_comp_ids:
            comp.description = f"{comp.description} (Updated to support {change_request.requirement_id})"

    # 4. Re-run validation on the updated blueprint
    new_validation = validate_blueprint(updated_reqs, updated_plan, updated_arch)

    # 5. Record version history
    new_version_num = blueprint.version + 1
    new_history = list(blueprint.version_history)
    new_history.append(BlueprintVersionSummary(
        version=new_version_num,
        created_at=blueprint.created_at,
        requirements_hash=updated_reqs.compute_hash(),
        plan_hash=updated_plan.compute_hash(),
        architecture_hash=updated_arch.compute_hash(),
        quality_score=new_validation.overall_score,
        change_summary=f"Modified {change_request.requirement_id} ({impact_report.impact_level.value} Impact) - {impact_report.explanation[:100]}..."
    ))

    # Rebuild traceability graph
    traceability_service.build_graph(updated_reqs, updated_plan, updated_arch)

    return CompleteBlueprint(
        project_id=blueprint.project_id,
        project_name=blueprint.project_name,
        version=new_version_num,
        requirements=updated_reqs,
        project_plan=updated_plan,
        architecture=updated_arch,
        rag_recommendations=blueprint.rag_recommendations,
        validation_report=new_validation,
        version_history=new_history
    )
