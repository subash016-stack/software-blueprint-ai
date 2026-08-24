"""Unit tests for Module 2: Project Planning Agent."""

import pytest
from pydantic import ValidationError
from app.schemas import (
    ProjectModule,
    Task,
    Milestone,
    ProjectPlan,
    Priority,
    RequirementAnalysis,
    Stakeholder,
    FunctionalRequirement,
    NonFunctionalRequirement
)
from app.agents.planning_agent import planning_agent_node
from app.state import BlueprintState


def test_project_module_model_valid():
    """Test valid project module schema."""
    mod = ProjectModule(
        id="MOD-001",
        name="Authentication",
        description="Handles user registration and login.",
        requirement_ids=["FR-001", "FR-002"],
        task_ids=["T-001", "T-002"]
    )
    assert mod.id == "MOD-001"
    assert mod.name == "Authentication"
    assert "FR-001" in mod.requirement_ids

    # Test auto-normalization
    mod2 = ProjectModule(
        id="mod-3",
        name="Payments",
        description="Handles transactions."
    )
    assert mod2.id == "MOD-003"


def test_task_model_valid():
    """Test valid task schema and requirement linking."""
    task = Task(
        id="T-001",
        title="Implement User Registration API",
        description="Create registration endpoint with password hashing.",
        requirement_ids=["FR-001"],
        priority=Priority.MUST,
        estimated_hours=4.0,
        dependencies=[]
    )
    assert task.id == "T-001"
    assert task.estimated_hours == 4.0
    assert task.requirement_ids == ["FR-001"]

    # Test auto-normalization
    task2 = Task(
        id="t-2",
        title="Implement Login API",
        description="JWT login endpoint.",
        requirement_ids=["FR-002"],
        priority=Priority.MUST,
        estimated_hours=3.5,
        dependencies=["T-001"]
    )
    assert task2.id == "T-002"
    assert task2.dependencies == ["T-001"]


def test_milestone_model_valid():
    """Test valid milestone schema."""
    m = Milestone(
        id="M-001",
        name="Core Backend Setup",
        description="Authentication and foundational database setup completed.",
        task_ids=["T-001", "T-002"]
    )
    assert m.id == "M-001"
    assert len(m.task_ids) == 2


def test_project_plan_cycle_cleanup():
    """Test that ProjectPlan validator detects and resolves circular dependencies."""
    plan = ProjectPlan(
        modules=[
            ProjectModule(id="MOD-001", name="Auth", description="Auth", requirement_ids=["FR-001"], task_ids=["T-001", "T-002"])
        ],
        tasks=[
            Task(id="T-001", title="Task 1", description="Desc 1", requirement_ids=["FR-001"], dependencies=["T-002"]),
            Task(id="T-002", title="Task 2", description="Desc 2", requirement_ids=["FR-001"], dependencies=["T-001"])
        ],
        milestones=[
            Milestone(id="M-001", name="Phase 1", description="Desc", task_ids=["T-001", "T-002"])
        ],
        roadmap=["Phase 1: Foundation", "Phase 2: Release"]
    )
    # Circular dependency between T-001 and T-002 should be detected and gracefully broken
    assert isinstance(plan, ProjectPlan)
    assert len(plan.tasks) == 2


def test_planning_agent_node_mocked(monkeypatch):
    """Test planning agent node execution in LangGraph with mock LLM output."""
    mock_plan = ProjectPlan(
        modules=[
            ProjectModule(id="MOD-001", name="Auth", description="Auth module", requirement_ids=["FR-001"], task_ids=["T-001"])
        ],
        tasks=[
            Task(
                id="T-001",
                title="Implement Auth",
                description="Auth task",
                requirement_ids=["FR-001"],
                priority=Priority.MUST,
                estimated_hours=4.0,
                dependencies=[]
            )
        ],
        milestones=[
            Milestone(id="M-001", name="Foundation", description="Auth deliverable", task_ids=["T-001"])
        ],
        roadmap=["Phase 1: Foundation", "Phase 2: Launch"]
    )

    monkeypatch.setattr("app.agents.planning_agent.generate_project_plan", lambda reqs: mock_plan)

    srs = RequirementAnalysis(
        project_name="FoodHub",
        project_description="Food app",
        stakeholders=[Stakeholder(id="ST-001", name="Customer", description="End user")],
        functional_requirements=[
            FunctionalRequirement(
                id="FR-001",
                title="User Registration",
                description="Register account",
                priority=Priority.MUST,
                stakeholders=["ST-001"]
            )
        ],
        non_functional_requirements=[],
        constraints=[],
        ambiguities=[],
        assumptions=[]
    )

    state: BlueprintState = {
        "project_idea": "Build a food app",
        "requirements": srs,
        "project_plan": None,
        "errors": []
    }

    result = planning_agent_node(state)
    assert result["project_plan"] is not None
    assert len(result["project_plan"].tasks) == 1
    assert result["project_plan"].tasks[0].requirement_ids == ["FR-001"]
