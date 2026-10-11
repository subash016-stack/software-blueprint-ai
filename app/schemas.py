"""Data schemas and Pydantic validation models for Software Blueprint AI (Modules 1-6)."""

from datetime import datetime
from enum import Enum
import hashlib
import json
import re
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class Priority(str, Enum):
    """MoSCoW priority levels for requirements and tasks."""
    MUST = "Must"
    SHOULD = "Should"
    COULD = "Could"
    WONT = "Won't"


class NFRCategory(str, Enum):
    """Standard categories for non-functional requirements."""
    PERFORMANCE = "Performance"
    SECURITY = "Security"
    SCALABILITY = "Scalability"
    RELIABILITY = "Reliability"
    AVAILABILITY = "Availability"
    USABILITY = "Usability"
    MAINTAINABILITY = "Maintainability"


# ==========================================
# MODULE 1: REQUIREMENT SCHEMAS
# ==========================================

class Stakeholder(BaseModel):
    """Identified stakeholder in the software project."""
    id: str = Field(
        ...,
        description="Unique identifier for the stakeholder (e.g., ST-001)",
        examples=["ST-001"]
    )
    name: str = Field(
        ...,
        description="Name/role of the stakeholder (e.g., Customer, Restaurant, Administrator)",
        examples=["Customer"]
    )
    description: str = Field(
        ...,
        description="Detailed description of stakeholder's role and responsibilities"
    )

    @field_validator("id")
    @classmethod
    def validate_stakeholder_id(cls, v: str) -> str:
        if not re.match(r"^ST-\d{3,}$", v):
            if re.match(r"^(st|ST)-?\d+$", v):
                digits = re.findall(r"\d+", v)[0]
                return f"ST-{int(digits):03d}"
            raise ValueError(f"Stakeholder ID '{v}' must follow the format 'ST-001'.")
        return v


class FunctionalRequirement(BaseModel):
    """Specific, testable functional requirement."""
    id: str = Field(
        ...,
        description="Unique identifier for the functional requirement (e.g., FR-001)",
        examples=["FR-001"]
    )
    title: str = Field(
        ...,
        description="Concise title of the functional requirement",
        examples=["User Registration"]
    )
    description: str = Field(
        ...,
        description="Detailed, unambiguous, and testable requirement statement"
    )
    priority: Priority = Field(
        default=Priority.MUST,
        description="MoSCoW priority (Must, Should, Could, Won't)"
    )
    stakeholders: List[str] = Field(
        default_factory=list,
        description="List of stakeholder IDs associated with this requirement (e.g., ['ST-001'])"
    )

    @field_validator("id")
    @classmethod
    def validate_fr_id(cls, v: str) -> str:
        if not re.match(r"^FR-\d{3,}$", v):
            if re.match(r"^(fr|FR)-?\d+$", v):
                digits = re.findall(r"\d+", v)[0]
                return f"FR-{int(digits):03d}"
            raise ValueError(f"Functional Requirement ID '{v}' must follow the format 'FR-001'.")
        return v


class NonFunctionalRequirement(BaseModel):
    """Quality attribute or operational constraint requirement."""
    id: str = Field(
        ...,
        description="Unique identifier for the NFR (e.g., NFR-001)",
        examples=["NFR-001"]
    )
    category: str = Field(
        ...,
        description="Category such as Performance, Security, Scalability, Reliability, Availability, Usability, Maintainability"
    )
    description: str = Field(
        ...,
        description="Measurable or testable non-functional requirement specification"
    )
    priority: Priority = Field(
        default=Priority.MUST,
        description="MoSCoW priority (Must, Should, Could, Won't)"
    )

    @field_validator("id")
    @classmethod
    def validate_nfr_id(cls, v: str) -> str:
        if not re.match(r"^NFR-\d{3,}$", v):
            if re.match(r"^(nfr|NFR)-?\d+$", v):
                digits = re.findall(r"\d+", v)[0]
                return f"NFR-{int(digits):03d}"
            raise ValueError(f"Non-Functional Requirement ID '{v}' must follow the format 'NFR-001'.")
        return v


class Ambiguity(BaseModel):
    """Detected ambiguity in the user prompt with suggested clarification."""
    ambiguity: str = Field(
        ...,
        description="Description of the unclear or ambiguous term/statement in the project idea"
    )
    possible_clarification: str = Field(
        default="Clarify specific technical requirements and architectural scope with stakeholders.",
        description="Suggested question or direction to clarify the ambiguity"
    )

    @model_validator(mode="before")
    @classmethod
    def handle_raw_inputs(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {
                "ambiguity": data,
                "possible_clarification": "Clarify specific technical requirements and architectural scope with stakeholders."
            }
        if isinstance(data, dict):
            if "ambiguity" not in data and "description" in data:
                data["ambiguity"] = data["description"]
            if "possible_clarification" not in data and "clarification" in data:
                data["possible_clarification"] = data["clarification"]
            if "possible_clarification" not in data:
                data["possible_clarification"] = "Clarify specific technical requirements and architectural scope with stakeholders."
        return data


class RequirementAnalysis(BaseModel):
    """Structured Software Requirements Specification (SRS) produced by Module 1."""
    project_name: str = Field(
        ...,
        description="Inferred or given project name"
    )
    project_description: str = Field(
        ...,
        description="High-level overview of the system purpose and domain"
    )
    stakeholders: List[Stakeholder] = Field(
        default_factory=list,
        description="List of primary and secondary stakeholders"
    )
    functional_requirements: List[FunctionalRequirement] = Field(
        default_factory=list,
        description="Structured functional requirements (FR-xxx)"
    )
    non_functional_requirements: List[NonFunctionalRequirement] = Field(
        default_factory=list,
        description="Structured non-functional requirements (NFR-xxx)"
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Explicit or strongly implied technical, budgetary, or platform constraints"
    )
    ambiguities: List[Ambiguity] = Field(
        default_factory=list,
        description="Identified ambiguities requiring future clarification"
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Explicit assumptions made to establish a baseline design"
    )

    def compute_hash(self) -> str:
        """Compute deterministic SHA-256 fingerprint of the requirements."""
        dumped = json.dumps(self.model_dump(), sort_keys=True)
        return hashlib.sha256(dumped.encode("utf-8")).hexdigest()[:16]


# ==========================================
# MODULE 2: PROJECT PLANNING SCHEMAS
# ==========================================

class ProjectModule(BaseModel):
    """Logical subsystem or component grouping related requirements."""
    id: str = Field(
        ...,
        description="Unique identifier for the module (e.g., MOD-001)",
        examples=["MOD-001"]
    )
    name: str = Field(
        ...,
        description="Module name (e.g., Authentication, Order Management)",
        examples=["Authentication"]
    )
    description: str = Field(
        ...,
        description="Purpose and scope of this logical module"
    )
    requirement_ids: List[str] = Field(
        default_factory=list,
        description="List of functional requirement IDs mapped to this module (e.g., ['FR-001', 'FR-002'])"
    )
    task_ids: List[str] = Field(
        default_factory=list,
        description="List of task IDs belonging to this module (e.g., ['T-001', 'T-002'])"
    )

    @field_validator("id")
    @classmethod
    def validate_module_id(cls, v: str) -> str:
        if not re.match(r"^MOD-\d{3,}$", v):
            if re.match(r"^(mod|MOD)-?\d+$", v):
                digits = re.findall(r"\d+", v)[0]
                return f"MOD-{int(digits):03d}"
            raise ValueError(f"Module ID '{v}' must follow the format 'MOD-001'.")
        return v


class Task(BaseModel):
    """Specific development task addressing one or more functional requirements."""
    id: str = Field(
        ...,
        description="Unique identifier for the task (e.g., T-001)",
        examples=["T-001"]
    )
    title: str = Field(
        ...,
        description="Action-oriented task title (e.g., Implement User Registration API)"
    )
    description: str = Field(
        ...,
        description="Detailed technical description of implementation work"
    )
    requirement_ids: List[str] = Field(
        default_factory=list,
        description="IDs of functional requirements addressed by this task (e.g., ['FR-001'])"
    )
    priority: Priority = Field(
        default=Priority.MUST,
        description="MoSCoW priority (Must, Should, Could, Won't)"
    )
    estimated_hours: float = Field(
        default=4.0,
        ge=0.5,
        description="Estimated development effort in person-hours"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="List of prerequisite task IDs that must complete before this task can start (e.g., ['T-001'])"
    )

    @field_validator("id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        if not re.match(r"^T-\d{3,}$", v):
            if re.match(r"^(t|T)-?\d+$", v):
                digits = re.findall(r"\d+", v)[0]
                return f"T-{int(digits):03d}"
            raise ValueError(f"Task ID '{v}' must follow the format 'T-001'.")
        return v


class Milestone(BaseModel):
    """Major project milestone grouping deliverables."""
    id: str = Field(
        ...,
        description="Unique identifier for the milestone (e.g., M-001)",
        examples=["M-001"]
    )
    name: str = Field(
        ...,
        description="Milestone name (e.g., Requirements and Initial Design, Core Backend)"
    )
    description: str = Field(
        ...,
        description="Summary of capabilities unlocked at this milestone"
    )
    task_ids: List[str] = Field(
        default_factory=list,
        description="List of task IDs required to achieve this milestone"
    )

    @field_validator("id")
    @classmethod
    def validate_milestone_id(cls, v: str) -> str:
        if not re.match(r"^M-\d{3,}$", v):
            if re.match(r"^(m|M)-?\d+$", v):
                digits = re.findall(r"\d+", v)[0]
                return f"M-{int(digits):03d}"
            raise ValueError(f"Milestone ID '{v}' must follow the format 'M-001'.")
        return v


class ProjectPlan(BaseModel):
    """Structured development plan produced by Module 2."""
    modules: List[ProjectModule] = Field(
        default_factory=list,
        description="Logical modules grouping requirements and tasks"
    )
    tasks: List[Task] = Field(
        default_factory=list,
        description="Ordered list of development tasks with requirement mappings and dependencies"
    )
    milestones: List[Milestone] = Field(
        default_factory=list,
        description="Key deliverable milestones"
    )
    roadmap: List[str] = Field(
        default_factory=list,
        description="Ordered sequential development phases (e.g., ['Phase 1: Foundation', 'Phase 2: Core Backend'])"
    )

    def compute_hash(self) -> str:
        dumped = json.dumps(self.model_dump(), sort_keys=True)
        return hashlib.sha256(dumped.encode("utf-8")).hexdigest()[:16]

    @model_validator(mode="after")
    def validate_task_dependencies_and_cycles(self) -> "ProjectPlan":
        task_ids = {t.id for t in self.tasks}
        
        # 1. Verify dependencies reference existing tasks
        for task in self.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    task.dependencies = [d for d in task.dependencies if d in task_ids]

        # 2. Check for circular dependencies using DFS cycle detection
        adj = {t.id: list(t.dependencies) for t in self.tasks}
        visited = {}  # 0: unvisited, 1: visiting, 2: visited

        def has_cycle(node: str) -> bool:
            visited[node] = 1
            for neighbor in adj.get(node, []):
                if visited.get(neighbor, 0) == 1:
                    return True
                if visited.get(neighbor, 0) == 0 and has_cycle(neighbor):
                    return True
            visited[node] = 2
            return False

        for t_id in task_ids:
            if visited.get(t_id, 0) == 0:
                if has_cycle(t_id):
                    for task in self.tasks:
                        task.dependencies = [d for d in task.dependencies if d != t_id]

        return self


# ==========================================
# MODULE 3: ARCHITECTURE DESIGN SCHEMAS
# ==========================================

class ArchitectureStyle(str, Enum):
    """High-level architectural pattern."""
    LAYERED_MONOLITH = "Layered Modular Monolith"
    MICROSERVICES = "Microservices Architecture"
    EVENT_DRIVEN = "Event-Driven Architecture"
    CLEAN_HEXAGONAL = "Clean / Hexagonal Architecture"
    SERVERLESS = "Serverless / Cloud-Native Architecture"
    CQRS_EVENT_SOURCING = "CQRS and Event Sourcing"


class Container(BaseModel):
    """C4 Container representing a deployable software unit (Web App, API Gateway, Service, DB)."""
    id: str = Field(..., description="Unique container ID (e.g., CONT-001)")
    name: str = Field(..., description="Container name (e.g., Web Frontend, API Gateway, Order Service)")
    type: str = Field(..., description="Type: 'Frontend', 'Backend Service', 'Database', 'Message Broker', 'Cache', 'Worker'")
    technology: str = Field(..., description="Technology stack (e.g., React, FastAPI, PostgreSQL, Redis)")
    description: str = Field(..., description="Responsibilities and purpose of this container")


class ArchitectureComponent(BaseModel):
    """C4 Component representing a modular service, controller, or domain service within a container."""
    id: str = Field(..., description="Component ID (e.g., COMP-001)")
    name: str = Field(..., description="Component name (e.g., Authentication Service, Order Processing Service)")
    description: str = Field(..., description="Technical responsibilities and domain boundaries")
    requirement_ids: List[str] = Field(
        default_factory=list,
        description="Functional requirement IDs traced directly to this component (e.g., ['FR-001', 'FR-002'])"
    )
    module_id: Optional[str] = Field(
        default=None,
        description="Parent logical module ID from project plan (e.g., 'MOD-001')"
    )
    container_id: Optional[str] = Field(
        default=None,
        description="Parent deployable container ID"
    )
    tech_stack: List[str] = Field(
        default_factory=list,
        description="Specific libraries and frameworks used (e.g., ['Pydantic', 'SQLAlchemy', 'JWT'])"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Component IDs this component invokes or depends upon"
    )

    @field_validator("id")
    @classmethod
    def validate_comp_id(cls, v: str) -> str:
        if not re.match(r"^COMP-\d{3,}$", v):
            if re.match(r"^(comp|COMP)-?\d+$", v):
                digits = re.findall(r"\d+", v)[0]
                return f"COMP-{int(digits):03d}"
            raise ValueError(f"Component ID '{v}' must follow the format 'COMP-001'.")
        return v


class ArchitectureAPI(BaseModel):
    """REST/GraphQL/gRPC Endpoint defined in the architecture blueprint."""
    id: str = Field(..., description="API ID (e.g., API-001)")
    endpoint: str = Field(..., description="URI route path (e.g., /api/v1/auth/register)")
    method: str = Field(..., description="HTTP Method (GET, POST, PUT, DELETE, PATCH, etc.)")
    summary: str = Field(..., description="Summary of API action")
    component_id: str = Field(..., description="Owning Architecture Component ID (e.g., COMP-001)")
    requirement_ids: List[str] = Field(
        default_factory=list,
        description="Traced functional requirements satisfied by this endpoint"
    )
    request_schema: Optional[str] = Field(default=None, description="Overview of request payload")
    response_schema: Optional[str] = Field(default=None, description="Overview of response payload")

    @field_validator("id")
    @classmethod
    def validate_api_id(cls, v: str) -> str:
        if not re.match(r"^API-\d{3,}$", v):
            if re.match(r"^(api|API)-?\d+$", v):
                digits = re.findall(r"\d+", v)[0]
                return f"API-{int(digits):03d}"
            raise ValueError(f"API ID '{v}' must follow the format 'API-001'.")
        return v


class ArchitectureDatabase(BaseModel):
    """Database or persistent storage entity in the architecture blueprint."""
    id: str = Field(..., description="Database ID (e.g., DB-001)")
    name: str = Field(..., description="Database name or entity model name")
    engine: str = Field(..., description="Engine technology (e.g., PostgreSQL, Redis, Qdrant, MongoDB)")
    type: str = Field(..., description="Type: Relational, Vector Store, Key-Value Cache, Document Store")
    schema_overview: str = Field(..., description="Key tables, collections, or indexes")
    component_ids: List[str] = Field(
        default_factory=list,
        description="Architecture component IDs interacting with this database"
    )

    @field_validator("id")
    @classmethod
    def validate_db_id(cls, v: str) -> str:
        if not re.match(r"^DB-\d{3,}$", v):
            if re.match(r"^(db|DB)-?\d+$", v):
                digits = re.findall(r"\d+", v)[0]
                return f"DB-{int(digits):03d}"
            raise ValueError(f"Database ID '{v}' must follow the format 'DB-001'.")
        return v


class ArchitectureDecisionRecord(BaseModel):
    """Architecture Decision Record (ADR) capturing trade-offs, alternatives, and rationale."""
    id: str = Field(default="ADR-001", description="ADR ID (e.g., ADR-001)")
    title: str = Field(..., description="Title of the architectural decision")
    status: str = Field(default="Accepted", description="Status: Accepted, Proposed, Superseded")
    context: str = Field(..., description="Problem context and architectural driving factors")
    decision: str = Field(..., description="The chosen architecture decision or pattern")
    rationale: str = Field(..., description="Technical justification for this decision")
    alternatives: List[str] = Field(default_factory=list, description="Alternative solutions considered")
    rejected_alternatives: List[str] = Field(default_factory=list, description="Why alternatives were rejected")
    consequences: str = Field(default="", description="Positive and negative trade-offs of this decision")
    requirement_ids: List[str] = Field(default_factory=list, description="Linked functional or non-functional requirement IDs")
    evidence_ids: List[str] = Field(default_factory=list, description="Linked RAG citation IDs (e.g. ['EVID-001'])")
    confidence: float = Field(default=0.92, ge=0.0, le=1.0, description="Confidence score")

    @field_validator("id")
    @classmethod
    def validate_adr_id(cls, v: str) -> str:
        if not re.match(r"^ADR-\d{3,}$", v):
            if re.match(r"^(adr|ADR)-?\d+$", v):
                digits = re.findall(r"\d+", v)[0]
                return f"ADR-{int(digits):03d}"
            return "ADR-001"
        return v


class TechStackItem(BaseModel):
    """Detailed justification, trade-off rationale, and literature citation for a chosen technology in the tech stack."""
    layer: str = Field(..., description="Architecture tier (e.g., 'Backend Framework', 'Relational Persistence', 'Cache Layer', 'Vector Knowledge Store', 'Frontend UI', 'Security & Identity')")
    technology: str = Field(..., description="Selected technology name (e.g., 'FastAPI', 'PostgreSQL 16', 'Redis 7', 'React 18', 'Qdrant')")
    category: str = Field(default="Core Stack", description="Category: 'Framework', 'Data Store', 'Performance', 'Security', 'User Interface'")
    decision_rationale: str = Field(..., description="In-depth explanation of why this specific technology was chosen over alternatives")
    pros: List[str] = Field(default_factory=list, description="Key technical advantages in this system context")
    tradeoffs: str = Field(..., description="Engineering trade-offs and operational constraints acknowledged")
    rag_citation: Optional[str] = Field(default=None, description="Linked architectural guide or evidence code (e.g., 'ARCH-001', 'DATA-001', 'SCALE-001', 'SEC-001')")


class ArchitectureBlueprint(BaseModel):
    """Complete Technical Architecture Blueprint produced by Module 3."""
    id: str = Field(default="ARCH-001", description="Architecture blueprint identifier")
    architecture_style: str = Field(
        default="Clean / Layered Modular Architecture",
        description="Overall architectural pattern"
    )
    overview: str = Field(..., description="Architectural design summary and structural rationale")
    containers: List[Container] = Field(default_factory=list, description="C4 deployable container tiers")
    components: List[ArchitectureComponent] = Field(default_factory=list, description="Modular software components")
    apis: List[ArchitectureAPI] = Field(default_factory=list, description="Core API specifications")
    databases: List[ArchitectureDatabase] = Field(default_factory=list, description="Data persistence and caching architecture")
    adrs: List[ArchitectureDecisionRecord] = Field(default_factory=list, description="Formal Architecture Decision Records (ADRs)")
    tech_stack_rationale: List[TechStackItem] = Field(default_factory=list, description="Detailed selection justifications for all technologies in the tech stack")
    security_strategy: str = Field(..., description="Authentication, authorization, TLS, data protection measures")
    scalability_strategy: str = Field(..., description="Load balancing, caching, asynchronous workers, horizontal scaling")
    deployment_topology: str = Field(..., description="Containerization, orchestration, and hosting topology")

    def compute_hash(self) -> str:
        dumped = json.dumps(self.model_dump(), sort_keys=True)
        return hashlib.sha256(dumped.encode("utf-8")).hexdigest()[:16]


# ==========================================
# MODULE 4: RAG RECOMMENDATION SCHEMAS
# ==========================================

class RAGEvidence(BaseModel):
    """Verified factual evidence chunk retrieved from the academic knowledge base."""
    source_id: str = Field(..., description="Document or citation identifier (e.g., ARCH-004)")
    title: str = Field(..., description="Title of academic document or pattern")
    category: str = Field(..., description="Category (e.g., Architecture Patterns, Security, Scalability)")
    section: str = Field(..., description="Document section or subsection heading")
    relevance_score: float = Field(default=0.9, ge=0.0, le=1.0, description="Cosine similarity / reranked confidence")
    excerpt: str = Field(..., description="Relevant factual text excerpt grounding the recommendation")


class GroundedRecommendation(BaseModel):
    """Architectural recommendation with strict evidence grounding and trade-off analysis."""
    topic: str = Field(..., description="Architecture topic (e.g., Data Persistence, Asynchronous Processing, Authentication)")
    recommendation: str = Field(..., description="Evidence-backed architectural recommendation")
    confidence: float = Field(default=0.90, ge=0.0, le=1.0, description="Grounding confidence score")
    tradeoffs: str = Field(..., description="Identified architectural trade-offs and potential pitfalls")
    evidence: List[RAGEvidence] = Field(default_factory=list, description="Academic source citations grounding this recommendation")


# ==========================================
# MODULE 5: VALIDATION & QUALITY SCORING
# ==========================================

class ValidationIssue(BaseModel):
    """Specific finding or anomaly identified during blueprint audit."""
    severity: Literal["CRITICAL", "WARNING", "INFO"] = "WARNING"
    code: str = Field(..., description="Error or audit code (e.g., UNTRACED_REQUIREMENT, INVALID_DEPENDENCY)")
    message: str = Field(..., description="Human-readable explanation of the issue")
    entity_id: Optional[str] = Field(default=None, description="Affected entity ID (e.g., FR-003, T-007)")
    recommendation: Optional[str] = Field(default=None, description="Suggested corrective action")


class ScoreExplanation(BaseModel):
    """Detailed explainability, calculation formula, and deduction trace for a quality score dimension."""
    dimension_name: str = Field(..., description="Name of the quality dimension (e.g. 'Requirements Specification Quality')")
    score: int = Field(..., ge=0, le=100, description="Quantitative score (0-100)")
    weight_pct: int = Field(..., description="Weight contribution percentage towards overall score")
    formula: str = Field(..., description="Mathematical calculation formula used")
    calculation_summary: str = Field(..., description="Step-by-step summary of how the score was computed")
    positive_factors: List[str] = Field(default_factory=list, description="List of positive engineering criteria that earned points")
    deductions: List[str] = Field(default_factory=list, description="List of deductions or penalties applied")
    actionable_guidance: str = Field(..., description="Actionable recommendation to improve this score")


class QualityScoreBreakdown(BaseModel):
    """Multi-dimensional software engineering quality score (0 to 100)."""
    requirement_quality: int = Field(default=90, ge=0, le=100)
    traceability_coverage: int = Field(default=95, ge=0, le=100)
    architecture_consistency: int = Field(default=90, ge=0, le=100)
    dependency_validity: int = Field(default=100, ge=0, le=100)
    nfr_coverage: int = Field(default=85, ge=0, le=100)
    rag_grounding_score: int = Field(default=90, ge=0, le=100)
    overall_score: int = Field(default=92, ge=0, le=100)


class ValidationReport(BaseModel):
    """Comprehensive blueprint audit and quality report produced by Module 5."""
    is_valid: bool = True
    overall_score: int = Field(default=90, ge=0, le=100)
    score_breakdown: QualityScoreBreakdown = Field(default_factory=QualityScoreBreakdown)
    score_explainability: Dict[str, ScoreExplanation] = Field(default_factory=dict)
    critical_issues: List[ValidationIssue] = Field(default_factory=list)
    warnings: List[ValidationIssue] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


# ==========================================
# MODULE 6: REQUIREMENT CHANGE IMPACT ANALYSIS
# ==========================================

class ImpactLevel(str, Enum):
    """Blast radius impact severity level."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ImpactReport(BaseModel):
    """Downstream blast radius analysis for a modified or added requirement."""
    changed_requirement_id: str = Field(..., description="Target changed requirement ID (e.g., FR-003)")
    change_type: Literal["MODIFIED", "ADDED", "DELETED"] = "MODIFIED"
    impact_level: ImpactLevel = ImpactLevel.MEDIUM
    affected_requirements: List[str] = Field(default_factory=list, description="Related functional requirement IDs")
    affected_modules: List[str] = Field(default_factory=list, description="Downstream affected module IDs (MOD-xxx)")
    affected_tasks: List[str] = Field(default_factory=list, description="Downstream affected development task IDs (T-xxx)")
    affected_components: List[str] = Field(default_factory=list, description="Affected architecture component IDs (COMP-xxx)")
    affected_apis: List[str] = Field(default_factory=list, description="Affected API endpoint IDs (API-xxx)")
    affected_milestones: List[str] = Field(default_factory=list, description="Affected project deliverable milestones (M-xxx)")
    effort_hours_delta: float = Field(default=0.0, description="Estimated change in total effort hours (+/-)")
    explanation: str = Field(..., description="Technical explanation of the downstream blast radius")
    recommended_actions: List[str] = Field(default_factory=list, description="Targeted re-engineering actions")


class RequirementChangeRequest(BaseModel):
    """Payload to propose a requirement change for impact analysis."""
    requirement_id: str = Field(..., description="Target functional requirement ID (e.g., FR-003)")
    new_title: Optional[str] = None
    new_description: str = Field(..., description="Updated requirement statement")
    new_priority: Optional[Priority] = None


# ==========================================
# VERSIONING & COMPLETE BLUEPRINT SCHEMAS
# ==========================================

class BlueprintVersionSummary(BaseModel):
    """Version metadata snapshot for history tracking."""
    version: int
    created_at: str
    requirements_hash: str
    plan_hash: str
    architecture_hash: str
    quality_score: int
    change_summary: Optional[str] = "Initial Blueprint Generation"


class CompleteBlueprint(BaseModel):
    """Full consolidated software engineering blueprint combining all modules."""
    project_id: str = "proj-default"
    project_name: str
    version: int = 1
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    requirements: RequirementAnalysis
    project_plan: ProjectPlan
    architecture: ArchitectureBlueprint
    rag_recommendations: List[GroundedRecommendation] = Field(default_factory=list)
    validation_report: Optional[ValidationReport] = None
    version_history: List[BlueprintVersionSummary] = Field(default_factory=list)
    requirements_hash: Optional[str] = None
    plan_hash: Optional[str] = None
    architecture_hash: Optional[str] = None
    execution_time_ms: Optional[float] = None
    agent_timings: Optional[Dict[str, float]] = Field(default_factory=dict)
    metrics: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def populate_hashes(self) -> "CompleteBlueprint":
        if not self.requirements_hash and self.requirements:
            self.requirements_hash = self.requirements.compute_hash()
        if not self.plan_hash and self.project_plan:
            self.plan_hash = self.project_plan.compute_hash()
        if not self.architecture_hash and self.architecture:
            self.architecture_hash = self.architecture.compute_hash()
        return self


# ==========================================
# API REQUEST & RESPONSE SCHEMAS
# ==========================================

class GenerateRequest(BaseModel):
    """Request payload for software blueprint generation."""
    project_idea: str = Field(
        ...,
        min_length=5,
        description="Natural language description of the software project idea",
        examples=["Build an online food delivery platform for customers, restaurants and delivery partners."]
    )
    project_name: Optional[str] = None


class GenerateResponse(BaseModel):
    """Complete response payload containing SRS and Project Plan (backwards compatible)."""
    requirements: RequirementAnalysis
    project_plan: ProjectPlan
    architecture: Optional[ArchitectureBlueprint] = None
    rag_recommendations: Optional[List[GroundedRecommendation]] = None
    validation_report: Optional[ValidationReport] = None
    version: int = 1
