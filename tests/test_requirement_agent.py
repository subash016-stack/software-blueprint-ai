"""Unit tests for Module 1: Requirement Analysis Agent."""

import pytest
from pydantic import ValidationError
from app.schemas import (
    Stakeholder,
    FunctionalRequirement,
    NonFunctionalRequirement,
    Ambiguity,
    RequirementAnalysis,
    Priority
)
from app.agents.requirement_agent import requirement_agent_node
from app.state import BlueprintState


def test_stakeholder_model_valid():
    """Test valid stakeholder schema instantiation and ID formatting."""
    st = Stakeholder(id="ST-001", name="Customer", description="End user who orders food.")
    assert st.id == "ST-001"
    assert st.name == "Customer"

    # Test ID auto-normalization
    st2 = Stakeholder(id="st-2", name="Restaurant", description="Food business.")
    assert st2.id == "ST-002"


def test_stakeholder_model_invalid_id():
    """Test rejection of invalid stakeholder ID."""
    with pytest.raises(ValidationError):
        Stakeholder(id="INVALID-ID", name="Customer", description="Description")


def test_functional_requirement_model_valid():
    """Test valid functional requirement schema."""
    fr = FunctionalRequirement(
        id="FR-001",
        title="User Registration",
        description="The customer shall be able to create an account with email and password.",
        priority=Priority.MUST,
        stakeholders=["ST-001"]
    )
    assert fr.id == "FR-001"
    assert fr.priority == Priority.MUST
    assert fr.stakeholders == ["ST-001"]

    # Test auto-normalization
    fr2 = FunctionalRequirement(
        id="fr-5",
        title="Place Order",
        description="Customer places an order.",
        priority=Priority.SHOULD,
        stakeholders=["ST-001"]
    )
    assert fr2.id == "FR-005"


def test_non_functional_requirement_model_valid():
    """Test valid non-functional requirement schema."""
    nfr = NonFunctionalRequirement(
        id="NFR-001",
        category="Security",
        description="User passwords must be hashed using bcrypt or Argon2.",
        priority=Priority.MUST
    )
    assert nfr.id == "NFR-001"
    assert nfr.category == "Security"
    assert nfr.priority == Priority.MUST


def test_requirement_analysis_schema():
    """Test complete RequirementAnalysis model construction."""
    req_analysis = RequirementAnalysis(
        project_name="FoodHub",
        project_description="Online food delivery platform.",
        stakeholders=[
            Stakeholder(id="ST-001", name="Customer", description="Orders food."),
            Stakeholder(id="ST-002", name="Restaurant", description="Prepares food."),
            Stakeholder(id="ST-003", name="Delivery Partner", description="Delivers food.")
        ],
        functional_requirements=[
            FunctionalRequirement(
                id="FR-001",
                title="User Registration",
                description="Allows users to register.",
                priority=Priority.MUST,
                stakeholders=["ST-001"]
            ),
            FunctionalRequirement(
                id="FR-002",
                title="Browse Menu",
                description="Allows customers to browse menus.",
                priority=Priority.MUST,
                stakeholders=["ST-001", "ST-002"]
            )
        ],
        non_functional_requirements=[
            NonFunctionalRequirement(
                id="NFR-001",
                category="Performance",
                description="API responses must be under 300ms for p95 requests.",
                priority=Priority.MUST
            )
        ],
        constraints=["Web and mobile target", "Python backend"],
        ambiguities=[
            Ambiguity(
                ambiguity="Delivery time expectation is unspecified.",
                possible_clarification="What is the target SLA for order delivery?"
            )
        ],
        assumptions=["Users have internet connectivity."]
    )

    assert req_analysis.project_name == "FoodHub"
    assert len(req_analysis.stakeholders) == 3
    assert len(req_analysis.functional_requirements) == 2
    assert len(req_analysis.non_functional_requirements) == 1
    assert len(req_analysis.ambiguities) == 1
    assert len(req_analysis.assumptions) == 1


def test_requirement_agent_node_mocked(monkeypatch):
    """Test requirement agent node execution in LangGraph with mock LLM output."""
    mock_srs = RequirementAnalysis(
        project_name="FoodHub",
        project_description="Food delivery app",
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
        non_functional_requirements=[
            NonFunctionalRequirement(
                id="NFR-001",
                category="Security",
                description="Encrypted passwords",
                priority=Priority.MUST
            )
        ],
        constraints=[],
        ambiguities=[],
        assumptions=["Users have smartphones"]
    )

    monkeypatch.setattr("app.agents.requirement_agent.generate_requirements", lambda idea: mock_srs)

    initial_state: BlueprintState = {
        "project_idea": "Build a food delivery app",
        "requirements": None,
        "project_plan": None,
        "errors": []
    }

    result = requirement_agent_node(initial_state)
    assert result["requirements"] is not None
    assert result["requirements"].project_name == "FoodHub"
    assert len(result["requirements"].functional_requirements) == 1
