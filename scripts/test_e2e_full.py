"""Comprehensive End-to-End Test Suite for Software Blueprint AI (Modules 1 to 6).

Executes the complete multi-agent generation pipeline, validates all schemas,
traceability relationships, RAG grounding, ADR evidence citations, NetworkX impact analysis,
versioning, export generation, and all FastAPI endpoints.
"""

import sys
import os
import json
import logging

# Ensure root workspace is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.graph import run_blueprint_generation
from app.schemas import (
    CompleteBlueprint,
    RequirementAnalysis,
    ProjectPlan,
    ArchitectureBlueprint,
    ValidationReport,
    GroundedRecommendation,
    RequirementChangeRequest,
    ImpactReport
)
from app.services.graph_service import traceability_service
from app.services.impact_service import analyze_requirement_impact, apply_targeted_regeneration
from app.services.export_service import export_markdown_dossier, export_openapi_spec, export_jira_backlog
from app.services.project_service import save_complete_blueprint, get_complete_blueprint, list_projects
from app.rag.retriever import get_indexed_documents_catalog, get_all_indexed_chunks, retrieve_relevant_evidence

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("e2e_tester")


def run_e2e_verification():
    logger.info("=================================================================")
    logger.info("STARTING SOFTWARE BLUEPRINT AI END-TO-END VERIFICATION")
    logger.info("=================================================================")

    # -------------------------------------------------------------
    # 1. TEST RAG KNOWLEDGE BASE & RETRIEVAL
    # -------------------------------------------------------------
    logger.info("[STEP 1/6] Verifying RAG Knowledge Base and Hierarchical Chunker...")
    docs = get_indexed_documents_catalog()
    assert len(docs) >= 7, f"Expected at least 7 indexed documents, got {len(docs)}"
    logger.info(f"✓ Catalog contains {len(docs)} documents:")
    for d in docs:
        logger.info(f"   - {d['document_id']}: {d['title']} ({d['chunks_count']} chunks)")

    chunks = get_all_indexed_chunks()
    assert len(chunks) > 0, "No chunks found in vector store"
    logger.info(f"✓ Total hierarchical vector chunks: {len(chunks)}")

    # Verify retrieval
    query = "Event-driven asynchronous messaging with Kafka and transactional outbox"
    retrieved = retrieve_relevant_evidence(query, top_k=3)
    assert len(retrieved) > 0, "Failed to retrieve evidence for architectural query"
    logger.info(f"✓ Retrieved top evidence: [{retrieved[0].source_id}] {retrieved[0].title} (Score: {retrieved[0].relevance_score})")

    # -------------------------------------------------------------
    # 2. RUN MULTI-AGENT GENERATION PIPELINE
    # -------------------------------------------------------------
    logger.info("[STEP 2/6] Executing Multi-Agent Pipeline (Modules 1 - 5)...")
    test_idea = "A real-time telemetry streaming and incident alerting engine for cloud microservices with sub-second latency"
    test_project_id = "proj-e2e-test"

    state = run_blueprint_generation(test_idea, project_id=test_project_id)
    errors = state.get("errors", [])
    if errors:
        logger.warning(f"Pipeline reported non-fatal notices: {errors}")

    reqs: RequirementAnalysis = state.get("requirements")
    plan: ProjectPlan = state.get("project_plan")
    arch: ArchitectureBlueprint = state.get("architecture")
    rag_recs = state.get("rag_recommendations", [])
    val_report: ValidationReport = state.get("validation_report")

    assert reqs is not None, "Module 1 Requirements failed"
    assert plan is not None, "Module 2 Planning failed"
    assert arch is not None, "Module 3 Architecture failed"
    assert val_report is not None, "Module 5 Validation failed"

    logger.info(f"✓ Module 1 SRS Produced: {len(reqs.functional_requirements)} FRs, {len(reqs.non_functional_requirements)} NFRs")
    logger.info(f"✓ Module 2 Plan Produced: {len(plan.modules)} Modules, {len(plan.tasks)} Tasks, Roadmap: {plan.roadmap}")
    logger.info(f"✓ Module 3 Architecture Produced: Style='{arch.architecture_style}', {len(arch.containers)} Containers, {len(arch.components)} Components, {len(arch.apis)} APIs")
    logger.info(f"✓ Module 3 ADRs: {len(arch.adrs)} records")
    for adr in arch.adrs:
        logger.info(f"   - {adr.id}: {adr.title} | Linked FRs: {adr.requirement_ids} | Evidence Citations: {adr.evidence_ids}")
        assert len(adr.evidence_ids) > 0, f"ADR {adr.id} missing RAG evidence citations!"

    logger.info(f"✓ Module 4 Grounded Recommendations: {len(rag_recs)} recommendations")
    for rec in rag_recs:
        logger.info(f"   - Topic: '{rec.topic}' (Confidence: {rec.confidence}) | Citations: {[e.source_id for e in rec.evidence]}")

    logger.info(f"✓ Module 5 Quality Score: {val_report.overall_score}/100 | Is Valid: {val_report.is_valid}")

    # -------------------------------------------------------------
    # 3. VERIFY TRACEABILITY GRAPH SERVICE
    # -------------------------------------------------------------
    logger.info("[STEP 3/6] Verifying Bidirectional Traceability Graph...")
    complete_bp = CompleteBlueprint(
        project_id=test_project_id,
        project_name=reqs.project_name or "Telemetry Platform",
        version=1,
        requirements=reqs,
        project_plan=plan,
        architecture=arch,
        rag_recommendations=rag_recs,
        validation_report=val_report,
        version_history=[]
    )
    save_complete_blueprint(complete_bp)

    traceability_service.build_graph(complete_bp.requirements, complete_bp.project_plan, complete_bp.architecture)
    graph_data = traceability_service.to_react_flow_graph()
    assert len(graph_data["nodes"]) > 0, "Traceability graph has zero nodes"
    assert len(graph_data["edges"]) > 0, "Traceability graph has zero edges"
    logger.info(f"✓ Traceability Graph built successfully with {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges")

    # -------------------------------------------------------------
    # 4. TEST MODULE 6: IMPACT ANALYSIS & VERSIONING
    # -------------------------------------------------------------
    logger.info("[STEP 4/6] Verifying Module 6 Impact Analysis & Targeted Regeneration...")
    target_fr = reqs.functional_requirements[0].id
    change_req = RequirementChangeRequest(
        requirement_id=target_fr,
        new_title="High-Throughput Distributed Telemetry Ingestion",
        new_description="Ingest over 1,000,000 telemetry metric events per second via distributed Kafka partitions."
    )

    impact = analyze_requirement_impact(complete_bp, change_req, generate_llm_explanation=False)
    assert impact.changed_requirement_id == target_fr
    logger.info(f"✓ Impact Analysis: Level = {impact.impact_level.value}")
    logger.info(f"   Affected Tasks: {impact.affected_tasks}")
    logger.info(f"   Affected Components: {impact.affected_components}")
    logger.info(f"   Affected APIs: {impact.affected_apis}")

    updated_bp = apply_targeted_regeneration(complete_bp, change_req, impact)
    assert updated_bp.version == 2, f"Expected version 2, got {updated_bp.version}"
    assert len(updated_bp.version_history) == 1, "Expected 1 snapshot in version history"
    logger.info(f"✓ Version Bump verified: v1 -> v{updated_bp.version} (Snapshot captured)")
    save_complete_blueprint(updated_bp)

    # -------------------------------------------------------------
    # 5. TEST EXPORT SERVICES
    # -------------------------------------------------------------
    logger.info("[STEP 5/6] Verifying Export Services (Dossier, OpenAPI, Jira)...")
    md_dossier = export_markdown_dossier(updated_bp)
    assert len(md_dossier) > 500, "Markdown dossier is empty or too short"
    assert "# Software Architecture Dossier" in md_dossier or updated_bp.project_name in md_dossier
    logger.info(f"✓ Markdown Dossier generated ({len(md_dossier)} characters)")

    openapi_spec = export_openapi_spec(updated_bp)
    assert openapi_spec.get("openapi") == "3.0.3", "Invalid OpenAPI spec version"
    assert "paths" in openapi_spec, "OpenAPI spec missing paths"
    logger.info(f"✓ OpenAPI 3.0.3 spec generated with {len(openapi_spec.get('paths', {}))} paths")

    jira_backlog = export_jira_backlog(updated_bp)
    assert "epics" in jira_backlog, "Jira backlog missing epics"
    assert "tasks" in jira_backlog, "Jira backlog missing tasks"
    logger.info(f"✓ Jira backlog generated with {len(jira_backlog.get('epics', []))} epics and {len(jira_backlog.get('tasks', []))} tasks")

    # -------------------------------------------------------------
    # 6. TEST ALL FASTAPI ENDPOINTS VIA TESTCLIENT
    # -------------------------------------------------------------
    logger.info("[STEP 6/6] Verifying All FastAPI REST Endpoints via TestClient...")
    client = TestClient(app)

    # Health
    r = client.get("/api/v1/health")
    assert r.status_code == 200, f"/health failed: {r.status_code}"
    assert r.json().get("status") in ("ok", "healthy")

    # Metrics
    r = client.get("/api/v1/metrics")
    assert r.status_code == 200

    # RAG Endpoints
    r = client.get("/api/v1/rag/documents")
    assert r.status_code == 200
    assert len(r.json()) >= 7

    r = client.get("/api/v1/rag/chunks")
    assert r.status_code == 200
    assert len(r.json()) > 0

    r = client.get("/api/v1/rag/qdrant-info")
    assert r.status_code == 200
    assert "dashboard_url" in r.json()

    # Project endpoints
    r = client.get("/api/v1/projects")
    assert r.status_code == 200
    projects = r.json()
    assert any(p["project_id"] == test_project_id for p in projects)

    r = client.get(f"/api/v1/projects/{test_project_id}/blueprint")
    assert r.status_code == 200
    assert r.json()["version"] == 2

    r = client.get(f"/api/v1/projects/{test_project_id}/architecture")
    assert r.status_code == 200
    assert "flow_graph" in r.json()

    r = client.get(f"/api/v1/projects/{test_project_id}/traceability")
    assert r.status_code == 200
    assert "graph" in r.json()
    assert r.json()["nodes_count"] > 0

    r = client.get(f"/api/v1/projects/{test_project_id}/validation")
    assert r.status_code == 200
    assert "overall_score" in r.json()

    r = client.get(f"/api/v1/projects/{test_project_id}/sources")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r = client.get(f"/api/v1/projects/{test_project_id}/versions")
    assert r.status_code == 200
    assert r.json()["current_version"] == 2

    # Export endpoints
    r = client.get(f"/api/v1/projects/{test_project_id}/export/markdown")
    assert r.status_code == 200
    assert "text/markdown" in r.headers["content-type"]

    r = client.get(f"/api/v1/projects/{test_project_id}/export/openapi")
    assert r.status_code == 200
    assert r.json().get("openapi") == "3.0.3"

    r = client.get(f"/api/v1/projects/{test_project_id}/export/jira")
    assert r.status_code == 200

    logger.info("=================================================================")
    logger.info("ALL END-TO-END TESTS PASSED WITH 100% SUCCESS!")
    logger.info("=================================================================")
    return True


if __name__ == "__main__":
    success = run_e2e_verification()
    if not success:
        sys.exit(1)
