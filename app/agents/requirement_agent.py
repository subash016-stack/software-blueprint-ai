"""Module 1: Requirement Analysis Agent.

Converts a natural-language software project idea into a structured
Software Requirements Specification (SRS) adhering to IEEE/ISO best practices.
"""

import logging
from typing import Dict, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from app.schemas import RequirementAnalysis, RequirementClassificationResult
from app.state import BlueprintState
from app.llm import invoke_structured

logger = logging.getLogger("software-blueprint-ai.requirements")

REQUIREMENT_SYSTEM_PROMPT = """You are a Principal Software Requirements Engineer with deep expertise in systems analysis, qualitative MoSCoW prioritization, and the quantitative RICE Prioritization Framework (Reach, Impact, Confidence, Effort).

Your task is to analyze the user's natural-language software project idea and produce a structured, high-traceability Software Requirements Specification (SRS).

GUIDELINES:
1. Stakeholders:
   - Identify 2-3 primary and administrative roles (Format IDs strictly as ST-001, ST-002).
2. Functional Requirements (FRs):
   - Generate exactly 3-4 concise, high-priority, testable functional requirements (Format IDs strictly as FR-001, FR-002, FR-003, FR-004).
   - Qualitative Prioritization (MoSCoW):
     - Assign MoSCoW priority: "Must", "Should", "Could", or "Won't".
   - Quantitative Prioritization (RICE Framework):
     - Calculate Reach: How many users/events will this feature affect in a given timeframe? (e.g. 5,000 customers per month).
     - Calculate Impact: How much will this contribute to primary goal? Standardized scale: 3.0 for massive impact, 2.0 for high, 1.0 for medium, 0.5 for low, 0.25 for minimal.
     - Calculate Confidence: How sure are you about your estimation data? (1.0 for 100% high confidence, 0.8 for 80% medium, 0.5 for 50% low/moonshot).
     - Calculate Effort: How much time will it take from product, design, and engineering? Measured in person-months or team-weeks (e.g. 0.5 to 3.0).
     - Formula: RICE Score = (Reach * Impact * Confidence) / Effort.
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
    """Analyze a project idea and return structured RequirementAnalysis with MoSCoW and RICE scores."""
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
    {{
      "id": "FR-001",
      "title": "string",
      "description": "string",
      "priority": "Must",
      "stakeholders": ["ST-001"],
      "rice": {{
        "reach": 5000,
        "impact": 2.0,
        "confidence": 0.8,
        "effort": 1.5
      }}
    }}
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

    analysis = invoke_structured(messages, RequirementAnalysis)
    analysis.populate_and_rank_rice_scores()
    return analysis



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


# ==========================================
# REQUIREMENT CLASSIFICATION & BENCHMARKING
# ==========================================

CLASSIFIER_SYSTEM_PROMPT = """You are an expert Systems Requirements Engineering Classifier specializing in IEEE 830 and ISO/IEC/IEEE 29148 standards.

Your task is to classify a given software requirement statement into either:
1. "FR" (Functional Requirement): Specifies WHAT the system must DO. Defines a functional behavior, service, action, feature, user interaction, data calculation, or system state transition (e.g. "allow users to reset passwords", "generate monthly sales reports", "lock account after 5 failed attempts", "allow administrators to disable accounts").
2. "NFR" (Non-Functional Requirement): Specifies HOW the system must PERFORM or BEHAVE under quality attributes, architectural constraints, or statutory mandates (e.g. performance/latency thresholds like "respond within 2 seconds", availability/uptime like "available 99.9% of the time", capacity/load like "support 5,000 concurrent users", security/encryption standards, and legal compliance obligations like "comply with applicable data protection laws").

You must return a valid JSON object matching this schema:
{
  "text": "original requirement statement",
  "predicted_label": "FR" or "NFR",
  "confidence": 0.95,
  "reasoning": "Clear 1-sentence technical explanation of why it is FR or NFR"
}
"""


def classify_requirement(
    requirement_text: str,
    req_id: Optional[str] = None,
    use_heuristic: bool = False,
    model_override: Optional[str] = None
) -> RequirementClassificationResult:
    """Classify a single requirement statement into FR or NFR using LLM with deterministic fallback."""
    if not requirement_text or not requirement_text.strip():
        raise ValueError("Requirement statement cannot be empty.")

    if use_heuristic:
        from app.benchmark.requirement_evaluator import heuristic_classify_requirement
        return heuristic_classify_requirement(requirement_text, req_id=req_id)

    prompt_content = f"""Classify the following software requirement into either 'FR' or 'NFR':

Requirement:
"{requirement_text.strip()}"

JSON Schema:
{{
  "id": "{req_id or ''}",
  "text": "{requirement_text.strip()}",
  "predicted_label": "FR",
  "confidence": 0.95,
  "reasoning": "Specifies an action, service, or behavior"
}}
"""

    messages = [
        SystemMessage(content=CLASSIFIER_SYSTEM_PROMPT),
        HumanMessage(content=prompt_content)
    ]

    try:
        result = invoke_structured(messages, RequirementClassificationResult, model_override=model_override)
        if req_id and not result.id:
            result.id = req_id
        return result
    except Exception as e:
        # Resilient fallback to deterministic rule-based classifier
        from app.benchmark.requirement_evaluator import heuristic_classify_requirement
        return heuristic_classify_requirement(requirement_text, req_id=req_id)


def batch_classify_requirements(
    requirements: List[Dict[str, str]],
    use_heuristic: bool = False,
    model_override: Optional[str] = None
) -> List[RequirementClassificationResult]:
    """Classify a batch of requirements, each with 'text' and optional 'id'."""
    results = []
    for item in requirements:
        text = item.get("text", "")
        req_id = item.get("id")
        results.append(classify_requirement(text, req_id=req_id, use_heuristic=use_heuristic, model_override=model_override))
    return results


