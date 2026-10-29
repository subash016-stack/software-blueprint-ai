"""Module 2: Project Planning Agent.

Consumes the structured requirements specification from Module 1
and generates an actionable engineering project plan with requirement traceability,
task breakdown, dependency scheduling, milestones, and a development roadmap.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from app.schemas import RequirementAnalysis, ProjectPlan
from app.state import BlueprintState
from app.llm import invoke_structured

PLANNING_SYSTEM_PROMPT = """You are a Lead Software Project Planner and Engineering Manager.

Your task is to take a structured Software Requirements Specification (SRS) and synthesize an actionable, high-traceability Software Engineering Project Plan.

IMPORTANT RULES:
1. Base your plan strictly on the provided requirements.
2. Modules:
   - Group requirements into exactly 2 cohesive logical modules (Format IDs strictly as MOD-001, MOD-002).
3. Tasks:
   - Generate exactly 4-5 concrete engineering tasks (Format IDs strictly as T-001, T-002, T-003, T-004, T-005).
   - Every task MUST explicitly link to one or more requirement IDs (e.g., ["FR-001"]).
   - Assign realistic estimated_hours (2.0 to 12.0 hours).
   - Define prerequisite task dependencies (e.g. ["T-001"]) ensuring a Directed Acyclic Graph (DAG) with NO circular dependencies.
4. Milestones:
   - Group tasks into 2 deliverable milestones (Format IDs strictly as M-001, M-002).
5. Roadmap:
   - Provide a 3-4 phase high-level roadmap.

Return the result conforming strictly to the requested JSON schema. Keep descriptions crisp and technical.
"""


def generate_project_plan(requirements: RequirementAnalysis) -> ProjectPlan:
    """Transform structured RequirementAnalysis into an actionable ProjectPlan."""
    if not requirements or not requirements.functional_requirements:
        raise ValueError("Requirements specification is missing or contains no functional requirements.")

    # Format the input requirements into structured context for the planner
    requirements_json = requirements.model_dump_json(indent=2)

    prompt_content = f"""Synthesize a structured engineering project plan for the following Software Requirements Specification and output a valid JSON object matching this exact schema:

JSON Schema:
{{
  "modules": [
    {{
      "id": "MOD-001",
      "name": "string",
      "description": "string",
      "requirement_ids": ["FR-001"],
      "task_ids": ["T-001"]
    }}
  ],
  "tasks": [
    {{
      "id": "T-001",
      "title": "string",
      "description": "string",
      "requirement_ids": ["FR-001"],
      "priority": "Must",
      "estimated_hours": 4.0,
      "dependencies": []
    }}
  ],
  "milestones": [
    {{
      "id": "M-001",
      "name": "string",
      "description": "string",
      "task_ids": ["T-001"]
    }}
  ],
  "roadmap": [
    "Phase 1: string",
    "Phase 2: string"
  ]
}}

Software Requirements Specification:
{requirements_json}
"""

    messages = [
        SystemMessage(content=PLANNING_SYSTEM_PROMPT),
        HumanMessage(content=prompt_content),
    ]

    return invoke_structured(messages, ProjectPlan)



def planning_agent_node(state: BlueprintState) -> BlueprintState:
    """LangGraph node for Module 2: Project Planning Agent."""
    requirements = state.get("requirements")
    if not requirements:
        errors = list(state.get("errors", []))
        errors.append("PlanningAgent error: No requirements found in state to plan.")
        return {
            **state,
            "errors": errors
        }

    try:
        project_plan = generate_project_plan(requirements)
        # Calibrate RICE effort metrics in pure code using actual WBS task hours
        from app.services.rice_service import apply_manual_rice_algorithm
        requirements = apply_manual_rice_algorithm(requirements, project_plan=project_plan)
        return {
            **state,
            "requirements": requirements,
            "project_plan": project_plan,
        }
    except Exception as e:
        errors = list(state.get("errors", []))
        errors.append(f"PlanningAgent error: {str(e)}")
        return {
            **state,
            "errors": errors
        }
