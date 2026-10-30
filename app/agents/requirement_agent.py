"""Module 1: Requirement Analysis Agent.

Converts a natural-language software project idea into a structured
Software Requirements Specification (SRS) adhering to IEEE/ISO best practices.
"""

import logging
from typing import Dict, List, Optional
from langchain_core.messages import SystemMessage, HumanMessage
from app.schemas import (
    RequirementAnalysis,
    RequirementClassificationResult,
    FunctionalRequirement,
    NonFunctionalRequirement,
    Priority
)
from app.state import BlueprintState
from app.llm import invoke_structured

logger = logging.getLogger("software-blueprint-ai.requirements")

REQUIREMENT_SYSTEM_PROMPT = """You are a Principal Software Requirements Engineer with deep expertise in systems analysis and qualitative MoSCoW prioritization (Must, Should, Could, Won't).

Your task is to analyze the user's natural-language software project idea and produce a comprehensive, structured, high-traceability Software Requirements Specification (SRS).

MANDATORY RULES & GUIDELINES:
1. Stakeholders:
   - Identify 2-3 distinct primary, operational, and administrative roles (Format IDs strictly as ST-001, ST-002).
2. Functional Requirements (FRs) — MANDATORY QUANTITY (4 to 6 FRs):
   - CRITICAL: You MUST generate between 4 to 6 comprehensive, testable functional requirements (FR-001, FR-002, FR-003, FR-004, FR-005).
   - NEVER output only 1 or 2 functional requirements! Software projects require multiple functional workflows:
     * FR-001: Core Domain Transaction / Primary User Journey (Must)
     * FR-002: User Authentication, Registration, and Access Control (Must)
     * FR-003: Data Search, Filtering, and Record Management (Should)
     * FR-004: Administrative Monitoring, Audit Logging, or Reporting (Could)
   - Assign realistic MoSCoW priorities: "Must", "Should", "Could", or "Won't".
   - Map each requirement to relevant stakeholder IDs (e.g. ["ST-001"]).
3. Non-Functional Requirements (NFRs) — MANDATORY QUANTITY (3 to 4 NFRs):
   - CRITICAL: You MUST provide at least 3 to 4 distinct, measurable NFRs across different quality categories (NFR-001, NFR-002, NFR-003, NFR-004).
   - NEVER output only 1 NFR! Cover these distinct categories:
     * NFR-001 (Performance): Specific latency SLA (e.g., API response p95 < 200ms).
     * NFR-002 (Security): Encryption standards (e.g., AES-256 at rest, TLS 1.3, Argon2/bcrypt password hashing).
     * NFR-003 (Availability): Uptime and recovery targets (e.g., 99.9% uptime SLA with automated health checks).
     * NFR-004 (Scalability): Concurrency bounds (e.g., support 5,000 concurrent users without degradation).
4. Constraints & Assumptions:
   - Provide 1-2 technical/budgetary constraints and 1-2 scoping assumptions.
5. Ambiguity Detection:
   - Identify 1-2 potential ambiguities with clarifying questions.

Return the result conforming strictly to the requested JSON schema. Ensure descriptions are detailed, technical, and testable.
"""


def _ensure_minimum_requirements(analysis: RequirementAnalysis) -> RequirementAnalysis:
    """Safeguard to guarantee the SRS contains a rich set of at least 4 FRs and 3 NFRs."""
    existing_fr_ids = {fr.id for fr in analysis.functional_requirements}
    existing_nfr_ids = {nfr.id for nfr in analysis.non_functional_requirements}
    st_id = analysis.stakeholders[0].id if analysis.stakeholders else "ST-001"
    admin_st_id = analysis.stakeholders[1].id if len(analysis.stakeholders) > 1 else st_id

    # Supplemental candidate FRs if LLM output was too sparse
    candidate_frs = [
        FunctionalRequirement(
            id="FR-002",
            title="User Authentication and Account Security",
            description="The system shall allow users to securely register, authenticate via password/token, and manage their profile.",
            priority=Priority.MUST,
            stakeholders=[st_id]
        ),
        FunctionalRequirement(
            id="FR-003",
            title="Data Search, Filtering and Status Tracking",
            description="The system shall provide search, multi-attribute filtering, and real-time status tracking for primary business entities.",
            priority=Priority.SHOULD,
            stakeholders=[st_id]
        ),
        FunctionalRequirement(
            id="FR-004",
            title="Administrative Governance and Audit Logging",
            description="The system shall provide administrators with management controls, activity audit logging, and operational dashboards.",
            priority=Priority.COULD,
            stakeholders=[admin_st_id]
        )
    ]

    for cand in candidate_frs:
        if len(analysis.functional_requirements) >= 4:
            break
        # Assign next available ID
        cand_id = f"FR-{len(analysis.functional_requirements) + 1:03d}"
        if cand_id not in existing_fr_ids:
            cand.id = cand_id
            analysis.functional_requirements.append(cand)
            existing_fr_ids.add(cand_id)

    # Supplemental candidate NFRs if LLM output was too sparse
    candidate_nfrs = [
        NonFunctionalRequirement(
            id="NFR-001",
            category="Performance",
            description="API response latency shall not exceed 250ms for p95 requests under a baseline workload of 1,000 concurrent requests.",
            priority=Priority.MUST
        ),
        NonFunctionalRequirement(
            id="NFR-002",
            category="Security",
            description="All sensitive data at rest shall be encrypted using AES-256 and in-transit communications enforced over TLS 1.3.",
            priority=Priority.MUST
        ),
        NonFunctionalRequirement(
            id="NFR-003",
            category="Availability",
            description="The system shall maintain 99.9% uptime SLA with automated container health probes and failover mechanisms.",
            priority=Priority.SHOULD
        )
    ]

    existing_categories = {n.category.lower() for n in analysis.non_functional_requirements}
    for cand_nfr in candidate_nfrs:
        if len(analysis.non_functional_requirements) >= 3:
            break
        if cand_nfr.category.lower() not in existing_categories:
            cand_id = f"NFR-{len(analysis.non_functional_requirements) + 1:03d}"
            cand_nfr.id = cand_id
            analysis.non_functional_requirements.append(cand_nfr)
            existing_categories.add(cand_nfr.category.lower())

    return analysis


def generate_requirements(project_idea: str) -> RequirementAnalysis:
    """Analyze a project idea and return structured RequirementAnalysis with deterministic manual RICE scoring."""
    if not project_idea or not project_idea.strip():
        raise ValueError("Project idea cannot be empty.")

    prompt_content = f"""Analyze this software project idea and output a valid JSON object matching this exact schema:

CRITICAL: You MUST provide at least 4 to 6 Functional Requirements (FR-001 to FR-004+) and at least 3 to 4 Non-Functional Requirements (NFR-001 to NFR-003+). Do NOT output only 1 requirement.

JSON Schema:
{{
  "project_name": "string",
  "project_description": "string",
  "stakeholders": [
    {{"id": "ST-001", "name": "Primary User", "description": "End-user interacting with the service"}},
    {{"id": "ST-002", "name": "System Administrator", "description": "Manages system operations and security"}}
  ],
  "functional_requirements": [
    {{
      "id": "FR-001",
      "title": "Primary Core Domain Operation",
      "description": "The system shall execute the core business workflow with comprehensive input validation.",
      "priority": "Must",
      "stakeholders": ["ST-001"]
    }},
    {{
      "id": "FR-002",
      "title": "User Authentication and Access Control",
      "description": "The system shall allow users to securely register, authenticate, and manage their credentials.",
      "priority": "Must",
      "stakeholders": ["ST-001"]
    }},
    {{
      "id": "FR-003",
      "title": "Data Search, Querying and Filtering",
      "description": "The system shall allow users to search and filter records based on multi-criteria queries.",
      "priority": "Should",
      "stakeholders": ["ST-001"]
    }},
    {{
      "id": "FR-004",
      "title": "Administrative Governance and Audit Logging",
      "description": "The system shall record immutable audit logs and provide administration management tools.",
      "priority": "Could",
      "stakeholders": ["ST-002"]
    }}
  ],
  "non_functional_requirements": [
    {{"id": "NFR-001", "category": "Performance", "description": "API responses shall be under 200ms for p95 requests under peak load.", "priority": "Must"}},
    {{"id": "NFR-002", "category": "Security", "description": "All data at rest shall be encrypted with AES-256 and data in transit secured via TLS 1.3.", "priority": "Must"}},
    {{"id": "NFR-003", "category": "Availability", "description": "The platform shall maintain 99.9% availability with automated recovery.", "priority": "Should"}}
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
    
    # Guarantee rich requirement coverage
    analysis = _ensure_minimum_requirements(analysis)

    # Execute deterministic manual RICE prioritization in pure Python code
    from app.services.rice_service import apply_manual_rice_algorithm
    analysis = apply_manual_rice_algorithm(analysis, force_recalculate=True)
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


