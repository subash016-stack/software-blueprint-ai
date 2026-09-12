"""Tests for Module 5: Validation and Blueprint Quality Scoring."""

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
    ArchitectureDatabase
)
from app.validation.deterministic import run_deterministic_audit


@pytest.fixture
def valid_blueprint_data():
    reqs = RequirementAnalysis(
        project_name="ShopApp",
        project_description="E-commerce shopping application",
        stakeholders=[Stakeholder(id="ST-001", name="Shopper", description="Purchases products")],
        functional_requirements=[
            FunctionalRequirement(id="FR-001", title="Browse Catalog", description="View products", priority="Must", stakeholders=["ST-001"]),
            FunctionalRequirement(id="FR-002", title="Checkout", description="Purchase items", priority="Must", stakeholders=["ST-001"]),
            FunctionalRequirement(id="FR-003", title="Order History", description="View past orders", priority="Should", stakeholders=["ST-001"])
        ],
        non_functional_requirements=[
            NonFunctionalRequirement(id="NFR-001", category="Security", description="PCI DSS compliance", priority="Must"),
            NonFunctionalRequirement(id="NFR-002", category="Performance", description="Sub-200ms response time", priority="Must")
        ]
    )
    plan = ProjectPlan(
        modules=[
            ProjectModule(id="MOD-001", name="Catalog & Orders", description="Catalog", requirement_ids=["FR-001", "FR-002", "FR-003"], task_ids=["T-001", "T-002", "T-003"])
        ],
        tasks=[
            Task(id="T-001", title="Catalog API", description="Catalog endpoints", requirement_ids=["FR-001"], estimated_hours=4.0),
            Task(id="T-002", title="Checkout Service", description="Checkout flow", requirement_ids=["FR-002"], estimated_hours=8.0, dependencies=["T-001"]),
            Task(id="T-003", title="History Query", description="Query past orders", requirement_ids=["FR-003"], estimated_hours=4.0, dependencies=["T-002"])
        ],
        milestones=[
            Milestone(id="M-001", name="MVP Release", description="Working store", task_ids=["T-001", "T-002", "T-003"])
        ],
        roadmap=["Phase 1: Storefront MVP"]
    )
    arch = ArchitectureBlueprint(
        overview="Clean architecture shopping backend",
        containers=[Container(id="CONT-001", name="Backend API", type="Backend Service", technology="FastAPI", description="API")],
        components=[
            ArchitectureComponent(id="COMP-001", name="Catalog Service", description="Catalog", requirement_ids=["FR-001"], module_id="MOD-001", container_id="CONT-001"),
            ArchitectureComponent(id="COMP-002", name="Order Service", description="Orders", requirement_ids=["FR-002", "FR-003"], module_id="MOD-001", container_id="CONT-001")
        ],
        apis=[],
        databases=[ArchitectureDatabase(id="DB-001", name="PostgreSQL", engine="PostgreSQL", type="Relational", schema_overview="products", component_ids=["COMP-001", "COMP-002"])],
        security_strategy="JWT Auth",
        scalability_strategy="Redis Cache",
        deployment_topology="Docker"
    )
    return reqs, plan, arch


def test_deterministic_audit_valid_blueprint(valid_blueprint_data):
    reqs, plan, arch = valid_blueprint_data
    crit, warn, scores = run_deterministic_audit(reqs, plan, arch)
    assert len(crit) == 0
    assert scores.overall_score >= 85
    assert scores.dependency_validity == 100
    assert scores.traceability_coverage == 100


def test_deterministic_audit_broken_traceability(valid_blueprint_data):
    reqs, plan, arch = valid_blueprint_data
    # Add untraced requirement
    reqs.functional_requirements.append(
        FunctionalRequirement(id="FR-004", title="Wishlist", description="Save favorites", priority="Could", stakeholders=["ST-001"])
    )
    crit, warn, scores = run_deterministic_audit(reqs, plan, arch)
    assert any(c.code == "UNTRACED_REQUIREMENT_NO_TASK" for c in crit)
    assert scores.traceability_coverage < 100
