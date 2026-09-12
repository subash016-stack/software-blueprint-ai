"""Tests for Module 3: Architecture Design Agent and C4 Schemas."""

import pytest
from app.schemas import (
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
    ArchitectureAPI,
    ArchitectureDatabase
)
from app.agents.architecture_agent import generate_architecture_flow_graph


@pytest.fixture
def sample_srs_and_plan():
    reqs = RequirementAnalysis(
        project_name="FoodDelivery",
        project_description="Online food ordering and delivery system",
        stakeholders=[Stakeholder(id="ST-001", name="Customer", description="Places orders")],
        functional_requirements=[
            FunctionalRequirement(id="FR-001", title="User Login", description="Users log in with credentials", priority="Must", stakeholders=["ST-001"]),
            FunctionalRequirement(id="FR-002", title="Place Order", description="Users place food orders", priority="Must", stakeholders=["ST-001"])
        ],
        non_functional_requirements=[
            NonFunctionalRequirement(id="NFR-001", category="Security", description="JWT TLS encryption", priority="Must")
        ]
    )
    plan = ProjectPlan(
        modules=[
            ProjectModule(id="MOD-001", name="Auth", description="Auth Module", requirement_ids=["FR-001"], task_ids=["T-001"]),
            ProjectModule(id="MOD-002", name="Orders", description="Orders Module", requirement_ids=["FR-002"], task_ids=["T-002"])
        ],
        tasks=[
            Task(id="T-001", title="Setup Auth API", description="JWT setup", requirement_ids=["FR-001"], estimated_hours=4.0),
            Task(id="T-002", title="Setup Order API", description="Order flow", requirement_ids=["FR-002"], estimated_hours=6.0, dependencies=["T-001"])
        ],
        milestones=[
            Milestone(id="M-001", name="Alpha", description="Core system", task_ids=["T-001", "T-002"])
        ],
        roadmap=["Phase 1: Auth", "Phase 2: Orders"]
    )
    return reqs, plan


def test_architecture_blueprint_validation():
    blueprint = ArchitectureBlueprint(
        id="ARCH-001",
        architecture_style="Clean / Layered Modular Architecture",
        overview="High performance scalable microservices backend",
        containers=[
            Container(id="CONT-001", name="API Gateway", type="Backend Service", technology="FastAPI", description="Routes requests"),
            Container(id="CONT-002", name="Database", type="Database", technology="PostgreSQL", description="Relational store")
        ],
        components=[
            ArchitectureComponent(
                id="COMP-001",
                name="Auth Service",
                description="Handles authentication",
                requirement_ids=["FR-001"],
                module_id="MOD-001",
                container_id="CONT-001",
                tech_stack=["FastAPI", "JWT"]
            )
        ],
        apis=[
            ArchitectureAPI(
                id="API-001",
                endpoint="/api/v1/auth/login",
                method="POST",
                summary="User Login",
                component_id="COMP-001",
                requirement_ids=["FR-001"]
            )
        ],
        databases=[
            ArchitectureDatabase(
                id="DB-001",
                name="Main PostgreSQL",
                engine="PostgreSQL",
                type="Relational",
                schema_overview="users, orders tables",
                component_ids=["COMP-001"]
            )
        ],
        security_strategy="OAuth2 with JWT and HTTPS TLS 1.3",
        scalability_strategy="Stateless API containers behind load balancer",
        deployment_topology="Docker Compose with isolated network bridges"
    )

    assert blueprint.id == "ARCH-001"
    assert len(blueprint.components) == 1
    assert blueprint.components[0].requirement_ids == ["FR-001"]
    assert blueprint.apis[0].id == "API-001"
    assert blueprint.compute_hash() is not None


def test_generate_architecture_flow_graph():
    blueprint = ArchitectureBlueprint(
        overview="Sample Arch",
        containers=[Container(id="CONT-001", name="Backend API", type="Backend Service", technology="FastAPI", description="API")],
        components=[
            ArchitectureComponent(id="COMP-001", name="Auth Engine", description="Auth", requirement_ids=["FR-001"], container_id="CONT-001", dependencies=[])
        ],
        apis=[],
        databases=[
            ArchitectureDatabase(id="DB-001", name="PostgreSQL", engine="PostgreSQL", type="Relational", schema_overview="Users", component_ids=["COMP-001"])
        ],
        security_strategy="TLS",
        scalability_strategy="Horizontal",
        deployment_topology="Docker"
    )

    flow_data = generate_architecture_flow_graph(blueprint)
    assert "nodes" in flow_data
    assert "edges" in flow_data
    assert len(flow_data["nodes"]) >= 3  # container, component, database
    assert len(flow_data["edges"]) >= 2
