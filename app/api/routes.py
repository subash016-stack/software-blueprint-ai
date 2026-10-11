import logging
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from app.schemas import (
    CompleteBlueprint,
    RequirementAnalysis,
    ProjectPlan,
    ArchitectureBlueprint,
    ValidationReport,
    GroundedRecommendation,
    RequirementChangeRequest,
    ImpactReport,
    GenerateRequest,
    GenerateResponse
)
from app.graph import run_blueprint_generation
from app.services.graph_service import traceability_service
from app.agents.architecture_agent import generate_architecture_flow_graph
from app.services.impact_service import analyze_requirement_impact, apply_targeted_regeneration
from app.services.project_service import save_complete_blueprint, get_complete_blueprint, list_projects
from app.services.export_service import export_markdown_dossier, export_openapi_spec, export_jira_backlog
from app.llm.factory import MetricsTracker
from app.rag.retriever import get_indexed_documents_catalog, get_all_indexed_chunks, load_and_ingest_knowledge_base
from app.rag.qdrant_client import vector_store

logger = logging.getLogger("software-blueprint-ai.api")

router = APIRouter()


class CreateProjectRequest(BaseModel):
    project_name: Optional[str] = None
    project_idea: str = Field(..., min_length=5, description="Natural language project idea")


@router.get("/projects", tags=["Projects"], summary="List all projects")
async def get_projects():
    """List all generated projects and their latest version summaries."""
    return list_projects()


@router.post("/projects", response_model=CompleteBlueprint, status_code=status.HTTP_201_CREATED, tags=["Projects"], summary="Create and generate a new project blueprint")
def create_project(request: CreateProjectRequest):
    """Execute end-to-end multi-agent pipeline to generate a full engineering blueprint."""
    idea = request.project_idea.strip()
    project_id = f"proj-{uuid.uuid4().hex[:8]}"

    logger.info("Starting blueprint pipeline for project: %s", idea[:60])
    result_state = run_blueprint_generation(idea, project_id=project_id)

    errors = result_state.get("errors", [])
    if errors and not result_state.get("requirements"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blueprint generation failed: {'; '.join(errors)}"
        )

    reqs = result_state.get("requirements")
    plan = result_state.get("project_plan")
    arch = result_state.get("architecture")
    rag = result_state.get("rag_recommendations", [])
    val = result_state.get("validation_report")

    if not reqs or not plan or not arch:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Incomplete blueprint generation. Upstream agents did not produce expected artifacts."
        )

    name = request.project_name or reqs.project_name or "Software Project"

    blueprint = CompleteBlueprint(
        project_id=project_id,
        project_name=name,
        version=1,
        requirements=reqs,
        project_plan=plan,
        architecture=arch,
        rag_recommendations=rag,
        validation_report=val,
        version_history=[]
    )

    save_complete_blueprint(blueprint)
    return blueprint


@router.get("/projects/{project_id}", response_model=CompleteBlueprint, tags=["Projects"], summary="Get project by ID")
async def get_project(project_id: str):
    """Retrieve full project details by project ID."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return bp


@router.get("/projects/{project_id}/blueprint", response_model=CompleteBlueprint, tags=["Blueprint"], summary="Get complete blueprint")
async def get_blueprint(project_id: str):
    """Get complete consolidated blueprint."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return bp


@router.get("/projects/{project_id}/requirements", response_model=RequirementAnalysis, tags=["Requirements"], summary="Get Module 1 SRS")
async def get_requirements(project_id: str):
    """Get structured Software Requirements Specification (Module 1)."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return bp.requirements


@router.get("/projects/{project_id}/project-plan", response_model=ProjectPlan, tags=["Project Plan"], summary="Get Module 2 Plan")
async def get_project_plan(project_id: str):
    """Get structured engineering project plan (Module 2)."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return bp.project_plan


@router.get("/projects/{project_id}/architecture", tags=["Architecture"], summary="Get Module 3 Architecture & Flow Graph")
async def get_architecture(project_id: str):
    """Get Technical Architecture Blueprint and React Flow graph nodes/edges (Module 3)."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    flow_graph = generate_architecture_flow_graph(bp.architecture)
    return {
        "architecture": bp.architecture,
        "flow_graph": flow_graph
    }


@router.get("/projects/{project_id}/traceability", tags=["Traceability"], summary="Get Multi-Tier Traceability Matrix & Graph")
async def get_traceability(project_id: str, highlight: Optional[str] = Query(None, description="Comma-separated entity IDs to highlight")):
    """Get multi-tier traceability graph (ST -> FR -> MOD -> T -> COMP -> API -> M) in React Flow format."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    traceability_service.build_graph(bp.requirements, bp.project_plan, bp.architecture)
    highlight_set = set(highlight.split(",")) if highlight else set()
    graph_data = traceability_service.to_react_flow_graph(highlight_set)

    return {
        "project_id": project_id,
        "nodes_count": len(graph_data["nodes"]),
        "edges_count": len(graph_data["edges"]),
        "graph": graph_data
    }


@router.get("/projects/{project_id}/validation", response_model=ValidationReport, tags=["Validation"], summary="Get Module 5 Validation Report")
async def get_validation(project_id: str):
    """Get blueprint validation audit, issue breakdown, and quality scores (Module 5)."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return bp.validation_report


@router.get("/projects/{project_id}/sources", response_model=List[GroundedRecommendation], tags=["RAG Evidence"], summary="Get Module 4 Grounded RAG Recommendations")
async def get_rag_sources(project_id: str):
    """Get evidence-grounded architectural recommendations and literature citations (Module 4)."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return bp.rag_recommendations


@router.get("/rag/documents", tags=["RAG Knowledge Base"], summary="Get all indexed knowledge base documents")
async def get_rag_documents():
    """Return catalog of all indexed software architecture documents with metadata, citations, and sections."""
    return get_indexed_documents_catalog()


@router.get("/rag/chunks", tags=["RAG Knowledge Base"], summary="Get all indexed vector chunks")
async def get_rag_chunks():
    """Return all hierarchical knowledge chunks with context breadcrumbs, keywords, and excerpts."""
    return get_all_indexed_chunks()


@router.get("/rag/qdrant-info", tags=["RAG Knowledge Base"], summary="Get Qdrant Vector Engine status & dashboard instructions")
async def get_qdrant_info():
    """Return Qdrant connection status, dashboard URL, collection configuration, and vector stats."""
    return vector_store.get_status()


@router.post("/rag/reindex", tags=["RAG Knowledge Base"], summary="Re-index all documents into vector store")
async def reindex_rag_documents():
    """Trigger complete re-indexing of all knowledge documents into Qdrant / memory vector store."""
    count = load_and_ingest_knowledge_base()
    return {
        "status": "success",
        "chunks_ingested": count,
        "message": f"Successfully ingested {count} hierarchical chunks into vector store."
    }


@router.get("/projects/{project_id}/versions", tags=["Versioning"], summary="Get Blueprint Version History")
async def get_versions(project_id: str):
    """Get version timeline and snapshots."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return {
        "current_version": bp.version,
        "history": bp.version_history
    }


@router.post("/projects/{project_id}/requirements/{requirement_id}/impact", response_model=ImpactReport, tags=["Impact Analysis"], summary="Module 6: Analyze Requirement Change Impact")
def analyze_impact(project_id: str, requirement_id: str, change_req: RequirementChangeRequest):
    """Analyze the downstream blast radius resulting from a modified functional requirement using NetworkX."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    change_req.requirement_id = requirement_id
    impact_report = analyze_requirement_impact(bp, change_req, generate_llm_explanation=False)
    return impact_report


@router.post("/projects/{project_id}/refine", response_model=CompleteBlueprint, tags=["Impact Analysis"], summary="Module 6: Targeted Selective Regeneration to produce v2")
def refine_blueprint(project_id: str, change_req: RequirementChangeRequest):
    """Apply requirement change with Targeted Selective Regeneration to produce a new Blueprint Version."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")

    impact_report = analyze_requirement_impact(bp, change_req, generate_llm_explanation=False)
    updated_bp = apply_targeted_regeneration(bp, change_req, impact_report)
    save_complete_blueprint(updated_bp)
    return updated_bp


@router.get("/metrics", tags=["Observability"], summary="System Performance and Token Metrics")
async def get_metrics():
    """Get real-time observability metrics: LLM invocations, token savings, cache hit rate, latencies."""
    return MetricsTracker.get_summary()


@router.get("/projects/{project_id}/export/markdown", tags=["Export"], summary="Export full IEEE 830 Engineering Dossier in Markdown")
def export_project_markdown(project_id: str):
    """Generate and download complete Software Engineering Blueprint Dossier in Markdown."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    md_content = export_markdown_dossier(bp)
    return PlainTextResponse(content=md_content, media_type="text/markdown")


@router.get("/projects/{project_id}/export/openapi", tags=["Export"], summary="Export OpenAPI 3.0.3 specification JSON")
def export_project_openapi(project_id: str):
    """Generate and export OpenAPI 3.0.3 schema covering all architecture APIs."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return export_openapi_spec(bp)


@router.get("/projects/{project_id}/export/jira", tags=["Export"], summary="Export Jira / GitHub backlog JSON")
def export_project_jira(project_id: str):
    """Generate and export Jira / GitHub issue backlog schema with Epics, Stories, and Tasks."""
    bp = get_complete_blueprint(project_id)
    if not bp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project '{project_id}' not found.")
    return export_jira_backlog(bp)
