"""Tests for FastAPI REST Endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import (
    CompleteBlueprint,
    RequirementAnalysis,
    Stakeholder,
    FunctionalRequirement,
    NonFunctionalRequirement,
    ProjectPlan,
    ProjectModule,
    Task,
    Milestone,
    ArchitectureBlueprint,
    Container,
    ArchitectureComponent,
    ArchitectureDatabase
)
from app.services.project_service import save_complete_blueprint

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_project():
    bp = CompleteBlueprint(
        project_id="test-proj-99",
        project_name="TestApp",
        version=1,
        requirements=RequirementAnalysis(
            project_name="TestApp",
            project_description="Test project description",
            stakeholders=[Stakeholder(id="ST-001", name="User", description="Normal user")],
            functional_requirements=[
                FunctionalRequirement(id="FR-001", title="Login", description="User login", priority="Must", stakeholders=["ST-001"])
            ],
            non_functional_requirements=[
                NonFunctionalRequirement(id="NFR-001", category="Security", description="Auth security", priority="Must")
            ]
        ),
        project_plan=ProjectPlan(
            modules=[ProjectModule(id="MOD-001", name="Auth", description="Auth", requirement_ids=["FR-001"], task_ids=["T-001"])],
            tasks=[Task(id="T-001", title="Auth API", description="Build auth", requirement_ids=["FR-001"], estimated_hours=4.0)],
            milestones=[Milestone(id="M-001", name="M1", description="M1", task_ids=["T-001"])],
            roadmap=["Phase 1"]
        ),
        architecture=ArchitectureBlueprint(
            overview="Arch",
            containers=[Container(id="CONT-001", name="API", type="Backend Service", technology="FastAPI", description="API")],
            components=[ArchitectureComponent(id="COMP-001", name="Auth Service", description="Auth", requirement_ids=["FR-001"], module_id="MOD-001", container_id="CONT-001")],
            apis=[],
            databases=[ArchitectureDatabase(id="DB-001", name="DB", engine="PostgreSQL", type="Relational", schema_overview="users", component_ids=["COMP-001"])],
            security_strategy="JWT",
            scalability_strategy="Redis",
            deployment_topology="Docker"
        )
    )
    save_complete_blueprint(bp)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_project_blueprint():
    response = client.get("/projects/test-proj-99/blueprint")
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == "test-proj-99"
    assert data["requirements"]["project_name"] == "TestApp"


def test_get_architecture_and_flow_graph():
    response = client.get("/projects/test-proj-99/architecture")
    assert response.status_code == 200
    data = response.json()
    assert "architecture" in data
    assert "flow_graph" in data
    assert len(data["flow_graph"]["nodes"]) >= 1


def test_get_traceability_graph():
    response = client.get("/projects/test-proj-99/traceability")
    assert response.status_code == 200
    data = response.json()
    assert data["nodes_count"] >= 1
    assert "graph" in data


def test_impact_analysis_endpoint():
    payload = {
        "requirement_id": "FR-001",
        "new_title": "Biometric OAuth Login",
        "new_description": "Support biometric passkeys and WebAuthn credentials."
    }
    response = client.post("/projects/test-proj-99/requirements/FR-001/impact", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["changed_requirement_id"] == "FR-001"
    assert "affected_tasks" in data


def test_refine_endpoint_targeted_regeneration():
    payload = {
        "requirement_id": "FR-001",
        "new_title": "Biometric OAuth Login",
        "new_description": "Support biometric passkeys and WebAuthn credentials."
    }
    response = client.post("/projects/test-proj-99/refine", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == 2
    assert len(data["version_history"]) == 1


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_llm_calls" in data
    assert "cache_hit_rate_percent" in data
