"""Module 1: Requirement Analysis Agent.

Converts a natural-language software project idea into a structured
Software Requirements Specification (SRS) adhering to IEEE/ISO best practices.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from app.schemas import RequirementAnalysis
from app.state import BlueprintState
from app.llm import invoke_structured

REQUIREMENT_SYSTEM_PROMPT = """You are a Principal Software Requirements Engineer with deep expertise in systems analysis and specification.

Your task is to analyze the user's natural-language software project idea and produce a structured, high-traceability Software Requirements Specification (SRS).

GUIDELINES:
1. Stakeholders:
   - Identify 2-3 primary and administrative roles (Format IDs strictly as ST-001, ST-002).
2. Functional Requirements (FRs):
   - Generate exactly 3-4 concise, high-priority, testable functional requirements (Format IDs strictly as FR-001, FR-002, FR-003, FR-004).
   - Assign MoSCoW priorities: "Must", "Should", "Could", or "Won't".
   - Map each requirement to relevant stakeholder IDs (e.g. ["ST-001"]).
3. Non-Functional Requirements (NFRs):
   - Provide 2 measurable NFRs (Format IDs strictly as NFR-001, NFR-002).
4. Constraints & Assumptions:
   - Provide 1-2 platform/security constraints and 1-2 scoping assumptions.
5. Ambiguity Detection:
   - Identify 1-2 potential ambiguities with clarifying questions.

Return the result conforming strictly to the requested JSON schema. Keep descriptions crisp, technical, and concise.
"""


def generate_requirements(project_idea: str) -> RequirementAnalysis:
    """Analyze a project idea and return structured RequirementAnalysis."""
    if not project_idea or not project_idea.strip():
        raise ValueError("Project idea cannot be empty.")

    prompt_content = f"""Analyze this software project idea and output a valid JSON object matching this exact schema:

JSON Schema:
{{
  "project_name": "string",
  "project_description": "string",
  "stakeholders": [
    {{"id": "ST-001", "name": "string", "description": "string"}}
  ],
  "functional_requirements": [
    {{"id": "FR-001", "title": "string", "description": "string", "priority": "Must", "stakeholders": ["ST-001"]}}
  ],
  "non_functional_requirements": [
    {{"id": "NFR-001", "category": "Security", "description": "string", "priority": "Must"}}
  ],
  "constraints": ["string"],
  "ambiguities": [
    {{"ambiguity": "string", "possible_clarification": "string"}}
  ],
  "assumptions": ["string"]
}}

Project Idea:
"{project_idea.strip()}"
"""

    messages = [
        SystemMessage(content=REQUIREMENT_SYSTEM_PROMPT),
        HumanMessage(content=prompt_content),
    ]

    return invoke_structured(messages, RequirementAnalysis)



def requirement_agent_node(state: BlueprintState) -> BlueprintState:
    """LangGraph node for Module 1: Requirement Analysis Agent."""
    project_idea = state.get("project_idea", "")
    try:
        requirements = generate_requirements(project_idea)
        return {
            "project_idea": project_idea,
            "requirements": requirements,
            "errors": state.get("errors", [])
        }
    except Exception as e:
        errors = list(state.get("errors", []))
        errors.append(f"RequirementAgent error: {str(e)}")
        return {
            "project_idea": project_idea,
            "errors": errors
        }
