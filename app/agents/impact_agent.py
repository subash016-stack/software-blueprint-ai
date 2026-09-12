"""Module 6: Requirement Change Impact Analysis LangGraph Node."""

import logging
from app.state import BlueprintState
from app.schemas import RequirementChangeRequest, CompleteBlueprint
from app.services.impact_service import analyze_requirement_impact

logger = logging.getLogger("software-blueprint-ai.impact_agent")


def impact_agent_node(state: BlueprintState) -> BlueprintState:
    """LangGraph node for Module 6: Impact Analysis."""
    requirements = state.get("requirements")
    project_plan = state.get("project_plan")
    architecture = state.get("architecture")
    metadata = state.get("metadata", {}) or {}

    change_req_data = metadata.get("pending_change_request")
    if not change_req_data or not requirements or not project_plan or not architecture:
        return state

    try:
        change_request = RequirementChangeRequest.model_validate(change_req_data)
        blueprint = CompleteBlueprint(
            project_id=state.get("project_id", "proj-default"),
            project_name=requirements.project_name,
            version=state.get("version", 1) or 1,
            requirements=requirements,
            project_plan=project_plan,
            architecture=architecture,
            rag_recommendations=state.get("rag_recommendations", []) or [],
            validation_report=state.get("validation_report")
        )
        report = analyze_requirement_impact(blueprint, change_request)
        return {
            **state,
            "impact_report": report
        }
    except Exception as e:
        logger.error("ImpactAgent execution failed: %s", e)
        errors = list(state.get("errors", []))
        errors.append(f"ImpactAgent error: {str(e)}")
        return {**state, "errors": errors}
