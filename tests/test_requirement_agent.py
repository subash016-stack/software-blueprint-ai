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
    # Verify RICE score was auto-populated
    fr0 = result["requirements"].functional_requirements[0]
    assert fr0.rice is not None
    assert fr0.rice.score > 0
    assert fr0.rice.rank == 1


def test_rice_score_calculation_direct():
    """Test quantitative RICE formula: (Reach * Impact * Confidence) / Effort."""
    from app.schemas import RICEScore

    # Standard inputs: 5,000 customers/mo, Impact=2.0 (High), Confidence=80% (0.8), Effort=1.0 person-month
    rice1 = RICEScore(reach=5000.0, impact=2.0, confidence=0.8, effort=1.0)
    expected1 = (5000.0 * 2.0 * 0.8) / 1.0  # 8000.0
    assert rice1.score == expected1
    assert rice1.impact_label == "High (2.0)"
    assert rice1.confidence_label == "Medium (80%)"

    # Percentage confidence input: 100% passed as 100
    rice2 = RICEScore(reach=1000.0, impact=3.0, confidence=100.0, effort=2.0)
    expected2 = (1000.0 * 3.0 * 1.0) / 2.0  # 1500.0
    assert rice2.score == expected2
    assert rice2.impact_label == "Massive (3.0)"
    assert rice2.confidence_label == "High (100%)"

    # Minimal effort clamping (prevents division by zero)
    rice3 = RICEScore(reach=2000.0, impact=1.0, confidence=0.5, effort=0.0)
    assert rice3.score > 0  # Does not raise ZeroDivisionError


def test_requirement_analysis_auto_ranks_rice():
    """Test that RequirementAnalysis computes RICE scores and ranks backlog objectively."""
    from app.schemas import RICEScore

    fr_high = FunctionalRequirement(
        id="FR-001",
        title="Payment Gateway",
        description="Process credit cards",
        priority=Priority.MUST,
        rice=RICEScore(reach=10000.0, impact=3.0, confidence=1.0, effort=1.0)  # Score = 30,000
    )
    fr_mid = FunctionalRequirement(
        id="FR-002",
        title="Email Notifications",
        description="Send receipts",
        priority=Priority.SHOULD,
        rice=RICEScore(reach=5000.0, impact=1.0, confidence=0.8, effort=2.0)   # Score = 2,000
    )
    fr_low = FunctionalRequirement(
        id="FR-003",
        title="Dark Mode",
        description="Theme toggling",
        priority=Priority.COULD,
        rice=RICEScore(reach=1000.0, impact=0.5, confidence=0.5, effort=1.0)   # Score = 250
    )

    reqs = RequirementAnalysis(
        project_name="FinApp",
        project_description="Financial platform",
        stakeholders=[Stakeholder(id="ST-001", name="User", description="End user")],
        functional_requirements=[fr_mid, fr_high, fr_low],  # Intentionally unordered
        non_functional_requirements=[]
    )

    # FR-001 must be Rank #1 (score 30,000)
    assert fr_high.rice.rank == 1
    # FR-002 must be Rank #2 (score 2,000)
    assert fr_mid.rice.rank == 2
    # FR-003 must be Rank #3 (score 250)
    assert fr_low.rice.rank == 3


def test_manual_rice_reach_calculation():
    """Test manual Reach computation by stakeholder scope and MoSCoW multiplier."""
    from app.services.rice_service import calculate_manual_reach

    st_user = Stakeholder(id="ST-001", name="End Customer", description="General consumer.")
    st_admin = Stakeholder(id="ST-002", name="System Admin", description="Security and IT administrator.")
    st_ops = Stakeholder(id="ST-003", name="Fleet Dispatcher", description="Operator managing drivers.")

    # 1. Customer + Must -> Scope 1.0 * Mult 1.0 * 5000 = 5000
    fr_customer = FunctionalRequirement(
        id="FR-001", title="Browse Catalog", description="Search products.",
        priority=Priority.MUST, stakeholders=["ST-001"]
    )
    reach_cust = calculate_manual_reach(fr_customer, [st_user, st_admin, st_ops])
    assert reach_cust == 5000.0

    # 2. Admin + Must -> Scope 0.08 * Mult 1.0 * 5000 = 400
    fr_admin = FunctionalRequirement(
        id="FR-002", title="Admin Audit Logs", description="View audit entries.",
        priority=Priority.MUST, stakeholders=["ST-002"]
    )
    reach_admin = calculate_manual_reach(fr_admin, [st_user, st_admin, st_ops])
    assert reach_admin == 400.0

    # 3. Ops + Should -> Scope 0.35 * Mult 0.75 * 5000 = 1312.5 -> round to 1312
    fr_ops = FunctionalRequirement(
        id="FR-003", title="Dispatch Overview", description="Staff route controls.",
        priority=Priority.SHOULD, stakeholders=["ST-003"]
    )
    reach_ops = calculate_manual_reach(fr_ops, [st_user, st_admin, st_ops])
    assert reach_ops == 1312.0


def test_manual_rice_impact_calculation():
    """Test manual Impact computation by business criticality and MoSCoW tier."""
    from app.services.rice_service import calculate_manual_impact

    # Core driver + Must = 3.0 (Massive)
    fr_core = FunctionalRequirement(
        id="FR-001", title="Payment Checkout", description="Process secure payment card transactions.",
        priority=Priority.MUST
    )
    assert calculate_manual_impact(fr_core) == 3.0

    # Non-core + Must = 2.0 (High)
    fr_must = FunctionalRequirement(
        id="FR-002", title="User Profile", description="Edit profile username and bio.",
        priority=Priority.MUST
    )
    assert calculate_manual_impact(fr_must) == 2.0

    # Could = 0.5 (Low)
    fr_could = FunctionalRequirement(
        id="FR-003", title="Custom Avatars", description="Upload cartoon avatar images.",
        priority=Priority.COULD
    )
    assert calculate_manual_impact(fr_could) == 0.5


def test_manual_rice_confidence_calculation():
    """Test manual Confidence computation by ambiguity overlap and specification completeness."""
    from app.services.rice_service import calculate_manual_confidence

    amb = Ambiguity(
        ambiguity="Payment gateway webhook retry interval is unspecified.",
        possible_clarification="Should failed payment webhooks retry exponentially up to 3 times?"
    )

    # FR overlapping with payment ambiguity
    fr_amb = FunctionalRequirement(
        id="FR-001", title="Payment Webhook Handler",
        description="Listen to external payment webhook callbacks and mark order paid.",
        priority=Priority.MUST, stakeholders=["ST-001"]
    )
    conf_amb = calculate_manual_confidence(fr_amb, [amb])
    assert conf_amb < 1.0  # Penalized due to ambiguity overlap

    # Fully specified FR with no ambiguity overlap
    fr_clear = FunctionalRequirement(
        id="FR-002", title="User Password Reset",
        description="The customer shall receive an email with a secure time-limited token to reset their password.",
        priority=Priority.MUST, stakeholders=["ST-001"]
    )
    conf_clear = calculate_manual_confidence(fr_clear, [amb])
    assert conf_clear == 1.0  # 100% confidence


def test_manual_rice_effort_and_wbs_calibration():
    """Test manual Effort calculation and calibration against actual WBS task hours."""
    from app.services.rice_service import calculate_manual_effort
    from app.schemas import Task

    fr = FunctionalRequirement(
        id="FR-001", title="Biometric Authentication",
        description="Verify fingerprint or face recognition for real-time sign in.",
        priority=Priority.MUST, stakeholders=["ST-001", "ST-002"]
    )

    # Heuristic effort without tasks
    effort_raw = calculate_manual_effort(fr, tasks=None)
    assert effort_raw >= 1.0

    # Calibration with actual WBS tasks: 2 tasks totaling 32 hours -> 32 / 160 = 0.2 person-months
    t1 = Task(
        id="T-001", title="Biometric SDK Integration", description="Hook up native SDK",
        requirement_ids=["FR-001"], estimated_hours=16.0, dependencies=[]
    )
    t2 = Task(
        id="T-002", title="Biometric Auth API endpoint", description="Verify tokens",
        requirement_ids=["FR-001"], estimated_hours=16.0, dependencies=["T-001"]
    )
    effort_wbs = calculate_manual_effort(fr, tasks=[t1, t2])
    assert effort_wbs == 0.20  # Exactly 32 hrs / 160 hrs/pm = 0.2 person-months

