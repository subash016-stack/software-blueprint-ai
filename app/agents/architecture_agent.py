"""Module 3: Architecture Design Agent.

Consumes the structured SRS (Module 1) and Project Plan (Module 2)
to synthesize a comprehensive, grounded Technical Architecture Blueprint.
All components, APIs, and databases maintain strict bidirectional requirement traceability.
"""

import logging
from typing import Any, Dict, List
from langchain_core.messages import SystemMessage, HumanMessage

from app.schemas import (
    RequirementAnalysis,
    ProjectPlan,
    ArchitectureBlueprint
)
from app.state import BlueprintState
from app.llm.factory import invoke_structured
from app.cache.redis_client import cache_manager
from app.config import get_settings

logger = logging.getLogger("software-blueprint-ai.architecture")

ARCHITECTURE_SYSTEM_PROMPT = """You are a Principal Software Architect and Systems Designer.

Your task is to analyze the provided SRS and Project Plan to produce a grounded Technical Architecture Blueprint.

CRITICAL RULES & TRACEABILITY CONSTRAINTS:
1. Architectural Style:
   - Select an appropriate style (e.g. "Clean / Layered Modular Architecture", "Event-Driven Microservices").
2. C4 Containers:
   - Define exactly 2-3 deployable units (CONT-001: Web App, CONT-002: Backend API, CONT-003: Database).
3. Architecture Components:
   - Define exactly 2-3 decoupled service components (COMP-001, COMP-002, COMP-003).
   - Every component MUST reference `requirement_ids` (e.g. ["FR-001"]) and `module_id` ("MOD-001").
4. APIs & Endpoints:
   - Define exactly 2-3 REST endpoints (API-001, API-002, API-003) linked to their owning `component_id` and `requirement_ids`.
5. Databases & Storage:
   - Define 1 primary database (DB-001) with 2 core tables and schema descriptions.
6. Architecture Decision Records (ADRs):
   - Generate 1-2 formal ADRs (ADR-001, ADR-002) with context, decision, rationale, and alternatives.

Return the output conforming strictly to the requested JSON schema. Keep descriptions crisp and technical.
"""


def generate_architecture_blueprint(
    requirements: RequirementAnalysis,
    project_plan: ProjectPlan
) -> ArchitectureBlueprint:
    """Generate structured Architecture Blueprint with caching and strict traceability."""
    settings = get_settings()

    # 1. Check cache
    cache_input = {
        "req_hash": requirements.compute_hash(),
        "plan_hash": project_plan.compute_hash()
    }
    cache_key = cache_manager.build_cache_key(
        operation="architecture",
        input_data=cache_input,
        prompt_version=settings.architecture_prompt_version,
        schema_version=settings.schema_version
    )
    cached_result = cache_manager.get(cache_key)
    if cached_result:
        logger.info("Cache hit for architecture blueprint generation.")
        return ArchitectureBlueprint.model_validate(cached_result)

    # 2. Prepare focused context (do not dump massive prompt unnecessarily)
    fr_summary = [
        {"id": fr.id, "title": fr.title, "priority": fr.priority.value, "description": fr.description[:120]}
        for fr in requirements.functional_requirements
    ]
    nfr_summary = [
        {"id": nfr.id, "category": nfr.category, "description": nfr.description[:120]}
        for nfr in requirements.non_functional_requirements
    ]
    module_summary = [
        {"id": m.id, "name": m.name, "requirement_ids": m.requirement_ids}
        for m in project_plan.modules
    ]

    prompt_content = f"""Synthesize a structured technical architecture blueprint for:
Project Name: {requirements.project_name}
Project Description: {requirements.project_description}

Functional Requirements:
{fr_summary}

Non-Functional Requirements:
{nfr_summary}

Logical Subsystems / Modules:
{module_summary}

Constraints:
{requirements.constraints}

Output a valid JSON object matching this exact schema:
{{
  "id": "ARCH-001",
  "architecture_style": "string",
  "overview": "string",
  "containers": [
    {{"id": "CONT-001", "name": "string", "type": "Backend Service", "technology": "FastAPI", "description": "string"}}
  ],
  "components": [
    {{"id": "COMP-001", "name": "string", "description": "string", "requirement_ids": ["FR-001"], "module_id": "MOD-001", "container_id": "CONT-001", "tech_stack": ["FastAPI", "SQLAlchemy"], "dependencies": []}}
  ],
  "apis": [
    {{"id": "API-001", "endpoint": "/api/v1/resource", "method": "POST", "summary": "string", "component_id": "COMP-001", "requirement_ids": ["FR-001"]}}
  ],
  "databases": [
    {{"id": "DB-001", "name": "Main DB", "engine": "PostgreSQL", "type": "Relational", "schema_overview": "string", "component_ids": ["COMP-001"]}}
  ],
  "security_strategy": "string",
  "scalability_strategy": "string",
  "deployment_topology": "string"
}}
"""

    messages = [
        SystemMessage(content=ARCHITECTURE_SYSTEM_PROMPT),
        HumanMessage(content=prompt_content),
    ]

    blueprint = invoke_structured(messages, ArchitectureBlueprint)

    # 3. Post-process to ensure all components link to valid requirement IDs
    valid_fr_ids = {fr.id for fr in requirements.functional_requirements}
    for comp in blueprint.components:
        comp.requirement_ids = [r for r in comp.requirement_ids if r in valid_fr_ids]
        if not comp.requirement_ids and valid_fr_ids:
            # Fallback link to first FR if LLM omitted
            comp.requirement_ids = [list(valid_fr_ids)[0]]

    # 4. Cache result
    cache_manager.set(cache_key, blueprint.model_dump())
    return blueprint


def generate_architecture_flow_graph(architecture: ArchitectureBlueprint) -> Dict[str, Any]:
    """Deterministically convert structured Architecture Blueprint into React Flow nodes and edges."""
    nodes = []
    edges = []

    # Container Tier Nodes (Parent groups)
    x_offset = 50
    y_offset = 50

    container_positions = {}
    for idx, cont in enumerate(architecture.containers):
        cont_id = cont.id or f"CONT-{idx+1:03d}"
        pos_x = x_offset + (idx % 3) * 320
        pos_y = y_offset + (idx // 3) * 280
        container_positions[cont_id] = (pos_x, pos_y)

        nodes.append({
            "id": cont_id,
            "type": "containerNode",
            "position": {"x": pos_x, "y": pos_y},
            "data": {
                "id": cont_id,
                "label": cont.name,
                "type": cont.type,
                "technology": cont.technology,
                "description": cont.description
            }
        })

    # Component Nodes
    for idx, comp in enumerate(architecture.components):
        comp_id = comp.id or f"COMP-{idx+1:03d}"
        c_x = 100 + (idx % 4) * 240
        c_y = 350 + (idx // 4) * 160

        nodes.append({
            "id": comp_id,
            "type": "componentNode",
            "position": {"x": c_x, "y": c_y},
            "data": {
                "id": comp_id,
                "label": comp.name,
                "description": comp.description,
                "requirements": comp.requirement_ids,
                "tech_stack": comp.tech_stack,
                "module_id": comp.module_id or ""
            }
        })

        if comp.container_id and comp.container_id in container_positions:
            edges.append({
                "id": f"e-{comp.container_id}-{comp_id}",
                "source": comp.container_id,
                "target": comp_id,
                "animated": True,
                "label": "contains"
            })

        for dep in comp.dependencies:
            edges.append({
                "id": f"e-{comp_id}-{dep}",
                "source": comp_id,
                "target": dep,
                "label": "calls"
            })

    # Database Nodes
    for idx, db in enumerate(architecture.databases):
        db_id = db.id or f"DB-{idx+1:03d}"
        d_x = 150 + idx * 280
        d_y = 650

        nodes.append({
            "id": db_id,
            "type": "databaseNode",
            "position": {"x": d_x, "y": d_y},
            "data": {
                "id": db_id,
                "label": db.name,
                "engine": db.engine,
                "type": db.type,
                "schema_overview": db.schema_overview
            }
        })

        for comp_id in db.component_ids:
            edges.append({
                "id": f"e-{comp_id}-{db_id}",
                "source": comp_id,
                "target": db_id,
                "label": "persists to"
            })

    return {"nodes": nodes, "edges": edges}


def architecture_agent_node(state: BlueprintState) -> BlueprintState:
    """LangGraph node for Module 3: Architecture Design Agent."""
    requirements = state.get("requirements")
    project_plan = state.get("project_plan")

    if not requirements or not project_plan:
        errors = list(state.get("errors", []))
        errors.append("ArchitectureAgent error: Missing requirements or project plan in state.")
        return {**state, "errors": errors}

    try:
        blueprint = generate_architecture_blueprint(requirements, project_plan)
        return {
            **state,
            "architecture": blueprint,
            "architecture_hash": blueprint.compute_hash()
        }
    except Exception as e:
        logger.error("ArchitectureAgent execution failed: %s", e)
        errors = list(state.get("errors", []))
        errors.append(f"ArchitectureAgent error: {str(e)}")
        return {**state, "errors": errors}
