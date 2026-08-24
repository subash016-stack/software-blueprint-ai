"""Module 1: Requirement Analysis Agent.

Converts a natural-language software project idea into a structured
Software Requirements Specification (SRS) adhering to IEEE/ISO best practices.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from app.schemas import RequirementAnalysis
from app.state import BlueprintState
from app.llm import invoke_structured

REQUIREMENT_SYSTEM_PROMPT = """You are a Principal Software Requirements Engineer with deep expertise in systems analysis and specification.

Your task is to analyze the user's natural-language software project idea and produce a comprehensive, structured Software Requirements Specification (SRS).

GUIDELINES:
1. Stakeholders:
   - Identify all primary, secondary, and administrative roles.
   - Format IDs strictly as ST-001, ST-002, etc.
   - Provide clear, distinct descriptions for each role.

2. Functional Requirements (FRs):
   - Generate specific, unambiguous, testable functional requirements.
   - Format IDs strictly as FR-001, FR-002, etc.
   - Assign MoSCoW priorities: "Must", "Should", "Could", or "Won't".
   - Map each requirement to relevant stakeholder IDs (e.g. ["ST-001"]).
   - Avoid vague statements like "system should be fast or good". Every FR must describe an observable behavior.

3. Non-Functional Requirements (NFRs):
   - Categorize into Performance, Security, Scalability, Reliability, Availability, Usability, or Maintainability.
   - Format IDs strictly as NFR-001, NFR-002, etc.
   - Make NFRs measurable where reasonable (do not invent arbitrary metrics if not implied).

4. Constraints:
   - Identify technical, platform, security, or deployment constraints implied by the problem.

5. Ambiguity Detection:
   - Detect vague or under-specified statements in the user's input.
   - For each ambiguity, describe why it is ambiguous and provide a targeted clarifying question.

6. Assumptions:
   - Record explicit baseline assumptions made to scope the initial requirements.

Return the result conforming strictly to the requested JSON schema.
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
