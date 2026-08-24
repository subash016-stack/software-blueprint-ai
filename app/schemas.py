"""Data schemas and Pydantic validation models for Software Blueprint AI."""

from enum import Enum
import re
from typing import List, Literal, Optional
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
            # Also normalize if plain number or lowercase prefix
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
        ...,
        description="Suggested question or direction to clarify the ambiguity"
    )


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

    @model_validator(mode="after")
    def validate_task_dependencies_and_cycles(self) -> "ProjectPlan":
        task_ids = {t.id for t in self.tasks}
        
        # 1. Verify dependencies reference existing tasks
        for task in self.tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    # Clean up invalid dependency references if any generated by LLM
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
                    # If cycle detected, break the cycle gracefully by removing back-edges
                    for task in self.tasks:
                        task.dependencies = [d for d in task.dependencies if d != t_id]

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


class GenerateResponse(BaseModel):
    """Complete response payload containing SRS and Project Plan."""
    requirements: RequirementAnalysis
    project_plan: ProjectPlan
