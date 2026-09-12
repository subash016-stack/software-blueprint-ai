"""Tests for Module 6: Requirement Change Impact Analysis and Targeted Selective Regeneration."""

import pytest
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
    ArchitectureAPI,
    ArchitectureDatabase,
    RequirementChangeRequest
)
from app.services.graph_service import traceability_service
from app.services.impact_service import analyze_requirement_impact, apply_targeted_regeneration


@pytest.fixture
def base_complete_blueprint():
    reqs = RequirementAnalysis(
        project_name="FoodDelivery",
        project_description="Food delivery app",
        stakeholders=[Stakeholder(id="ST-001", name="Customer", description="Orders food")],
        functional_requirements=[
            FunctionalRequirement(id="FR-001", title="User Auth", description="Login system", priority="Must", stakeholders=["ST-001"]),
            FunctionalRequirement(id="FR-002", title="Place Order", description="Order food", priority="Must", stakeholders=["ST-001"]),
            FunctionalRequirement(id="FR-003", title="Payment Gateway", description="Credit card payments", priority="Must", stakeholders=["ST-001"])
        ],
        non_functional_requirements=[
            NonFunctionalRequirement(id="NFR-001", category="Security", description="PCI DSS", priority="Must")
        ]
    )
    plan = ProjectPlan(
        modules=[
            ProjectModule(id="MOD-001", name="Auth", description="Auth", requirement_ids=["FR-001"], task_ids=["T-001"]),
            ProjectModule(id="MOD-002", name="Orders", description="Orders", requirement_ids=["FR-002"], task_ids=["T-002"]),
            ProjectModule(id="MOD-003", name="Payments", description="Payments", requirement_ids=["FR-003"], task_ids=["T-003", "T-004"])
        ],
        tasks=[
            Task(id="T-001", title="Auth API", description="JWT setup", requirement_ids=["FR-001"], estimated_hours=4.0),
            Task(id="T-002", title="Order API", description="Order setup", requirement_ids=["FR-002"], estimated_hours=6.0, dependencies=["T-001"]),
            Task(id="T-003", title="Stripe Integration", description="Stripe checkout", requirement_ids=["FR-003"], estimated_hours=8.0, dependencies=["T-002"]),
            Task(id="T-004", title="Payment Webhooks", description="Webhook handler", requirement_ids=["FR-003"], estimated_hours=4.0, dependencies=["T-003"])
        ],
        milestones=[
            Milestone(id="M-001", name="Auth Setup", description="Auth milestone", task_ids=["T-001"]),
            Milestone(id="M-002", name="Order and Pay", description="Core commerce", task_ids=["T-002", "T-003", "T-004"])
        ],
        roadmap=["Phase 1: Foundation", "Phase 2: Core Platform"]
    )
    arch = ArchitectureBlueprint(
        overview="Clean architecture backend",
        containers=[Container(id="CONT-001", name="API Server", type="Backend Service", technology="FastAPI", description="API")],
        components=[
            ArchitectureComponent(id="COMP-001", name="Auth Service", description="Auth", requirement_ids=["FR-001"], module_id="MOD-001", container_id="CONT-001"),
            ArchitectureComponent(id="COMP-002", name="Order Service", description="Orders", requirement_ids=["FR-002"], module_id="MOD-002", container_id="CONT-001"),
            ArchitectureComponent(id="COMP-003", name="Payment Service", description="Payments", requirement_ids=["FR-003"], module_id="MOD-003", container_id="CONT-001")
        ],
        apis=[
            ArchitectureAPI(id="API-001", endpoint="/api/v1/payments/charge", method="POST", summary="Charge", component_id="COMP-003", requirement_ids=["FR-003"])
        ],
        databases=[
            ArchitectureDatabase(id="DB-001", name="PostgreSQL", engine="PostgreSQL", type="Relational", schema_overview="payments", component_ids=["COMP-003"])
        ],
        security_strategy="TLS, Token Auth",
        scalability_strategy="Redis Cache",
        deployment_topology="Docker"
    )
    return CompleteBlueprint(
        project_id="proj-food-01",
        project_name="FoodDelivery",
        version=1,
        requirements=reqs,
        project_plan=plan,
        architecture=arch
    )


def test_networkx_downstream_impact_analysis(base_complete_blueprint):
    bp = base_complete_blueprint
    traceability_service.build_graph(bp.requirements, bp.project_plan, bp.architecture)
    
    # Analyze impact on FR-003
    impact = traceability_service.analyze_downstream_impact("FR-003")
    
    assert "MOD-003" in impact["affected_modules"]
    assert "T-003" in impact["affected_tasks"]
    assert "T-004" in impact["affected_tasks"]
    assert "COMP-003" in impact["affected_components"]
    assert "API-001" in impact["affected_apis"]
    assert "M-002" in impact["affected_milestones"]
    # Unaffected entities should NOT be in affected list
    assert "MOD-001" not in impact["affected_modules"]
    assert "T-001" not in impact["affected_tasks"]
    assert "COMP-001" not in impact["affected_components"]


def test_targeted_selective_regeneration_versioning(base_complete_blueprint):
    bp = base_complete_blueprint
    change_req = RequirementChangeRequest(
        requirement_id="FR-003",
        new_title="Subscription & Split Billing",
        new_description="Add support for recurring subscription meal plans and split-bill payments among friends."
    )
    impact_report = analyze_requirement_impact(bp, change_req, generate_llm_explanation=False)
    assert impact_report.changed_requirement_id == "FR-003"

    v2_blueprint = apply_targeted_regeneration(bp, change_req, impact_report)
    
    assert v2_blueprint.version == 2
    # Verify target requirement is updated
    updated_fr3 = next(fr for fr in v2_blueprint.requirements.functional_requirements if fr.id == "FR-003")
    assert "Subscription" in updated_fr3.title
    
    # Verify unaffected requirements were kept unchanged
    fr1 = next(fr for fr in v2_blueprint.requirements.functional_requirements if fr.id == "FR-001")
    assert fr1.title == "User Auth"

    # Verify unaffected task T-001 was untouched
    t1 = next(t for t in v2_blueprint.project_plan.tasks if t.id == "T-001")
    assert t1.estimated_hours == 4.0

    # Verify affected task T-003 effort was updated
    t3 = next(t for t in v2_blueprint.project_plan.tasks if t.id == "T-003")
    assert "[Refined for FR-003" in t3.description
    assert t3.estimated_hours > 8.0

    # Verify version history snapshot recorded
    assert len(v2_blueprint.version_history) == 1
    assert v2_blueprint.version_history[0].version == 2
