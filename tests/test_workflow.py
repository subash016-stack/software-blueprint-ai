"""Integration tests for LangGraph blueprint workflow and FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.graph import build_blueprint_graph
from app.schemas import (
    RequirementAnalysis,
    ProjectPlan,
    Stakeholder,
    FunctionalRequirement,
    NonFunctionalRequirement,
    ProjectModule,
    Task,
    Milestone,
    Priority
)


@pytest.fixture
def client():
    """TestClient for FastAPI app."""
    return TestClient(app)


def test_graph_structure():
    """Test that LangGraph compiles and contains required nodes and topology."""
    graph = build_blueprint_graph()
    assert graph is not None
    # Verify graph node names
    nodes = graph.nodes
    assert "requirement_agent" in nodes
    assert "planning_agent" in nodes


def test_health_endpoint(client):
    """Test GET /health returns 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_frontend_endpoint(client):
    """Test GET / serves the frontend dashboard HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Software Blueprint AI" in response.text



def test_generate_endpoint_validation_error(client):
    """Test POST /generate with invalid/empty project idea returns 400 or 422."""
    # Empty string
    response = client.post("/generate", json={"project_idea": ""})
    assert response.status_code in [400, 422]

    # Too short
    response2 = client.post("/generate", json={"project_idea": "abc"})
    assert response2.status_code in [400, 422]


def test_generate_endpoint_success_mocked(client, monkeypatch):
    """Test POST /generate end-to-end with mocked LLM outputs."""
    mock_srs = RequirementAnalysis(
        project_name="Online Food Delivery Platform",
        project_description="A platform connecting customers, restaurants, and couriers.",
        stakeholders=[
            Stakeholder(id="ST-001", name="Customer", description="Places orders"),
            Stakeholder(id="ST-002", name="Restaurant", description="Manages menus and food preparation"),
            Stakeholder(id="ST-003", name="Delivery Partner", description="Delivers orders")
        ],
        functional_requirements=[
            FunctionalRequirement(
                id="FR-001",
                title="User Authentication",
                description="Register and login with role-based access.",
                priority=Priority.MUST,
                stakeholders=["ST-001", "ST-002", "ST-003"]
            ),
            FunctionalRequirement(
                id="FR-002",
                title="Browse and Search Menus",
                description="Customers can search food items and filter by cuisine.",
                priority=Priority.MUST,
                stakeholders=["ST-001"]
            )
        ],
        non_functional_requirements=[
            NonFunctionalRequirement(
                id="NFR-001",
                category="Security",
                description="All sensitive customer data encrypted at rest.",
                priority=Priority.MUST
            )
        ],
        constraints=["Local deployment with Ollama"],
        ambiguities=[],
        assumptions=["Users have mobile or desktop browsers"]
    )

    mock_plan = ProjectPlan(
        modules=[
            ProjectModule(
                id="MOD-001",
                name="Authentication & Authorization",
                description="User management and JWT auth",
                requirement_ids=["FR-001"],
                task_ids=["T-001"]
            ),
            ProjectModule(
                id="MOD-002",
                name="Catalog & Search",
                description="Menu listing and search",
                requirement_ids=["FR-002"],
                task_ids=["T-002"]
            )
        ],
        tasks=[
            Task(
                id="T-001",
                title="Implement Auth Endpoints",
                description="Create registration and login APIs",
                requirement_ids=["FR-001"],
                priority=Priority.MUST,
                estimated_hours=4.0,
                dependencies=[]
            ),
            Task(
                id="T-002",
                title="Implement Menu Search Endpoint",
                description="Create catalog search API",
                requirement_ids=["FR-002"],
                priority=Priority.MUST,
                estimated_hours=6.0,
                dependencies=["T-001"]
            )
        ],
        milestones=[
            Milestone(
                id="M-001",
                name="Foundation & Auth",
                description="Authentication and database setup",
                task_ids=["T-001"]
            ),
            Milestone(
                id="M-002",
                name="Core Catalog Services",
                description="Search and catalog APIs",
                task_ids=["T-002"]
            )
        ],
        roadmap=[
            "Phase 1: Foundation & Auth Setup",
            "Phase 2: Menu Catalog & Search",
            "Phase 3: Integration & Testing"
        ]
    )

    monkeypatch.setattr("app.agents.requirement_agent.generate_requirements", lambda idea: mock_srs)
    monkeypatch.setattr("app.agents.planning_agent.generate_project_plan", lambda reqs: mock_plan)

    payload = {
        "project_idea": "Build an online food delivery platform for customers, restaurants and delivery partners."
    }

    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "requirements" in data
    assert "project_plan" in data
    assert data["requirements"]["project_name"] == "Online Food Delivery Platform"
    assert len(data["requirements"]["stakeholders"]) == 3
    assert len(data["requirements"]["functional_requirements"]) == 2
    assert len(data["project_plan"]["modules"]) == 2
    assert len(data["project_plan"]["tasks"]) == 2
    assert data["project_plan"]["tasks"][0]["requirement_ids"] == ["FR-001"]
