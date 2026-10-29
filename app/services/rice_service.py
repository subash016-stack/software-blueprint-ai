"""
app/services/rice_service.py
Deterministic Manual RICE Prioritization Engine for Software Blueprint AI.

Calculates the quantitative RICE Framework metrics manually in pure Python code
without relying on LLM estimation or arithmetic hallucinations:
- Reach (R): Computed from target stakeholder roles, user base cohorts, and MoSCoW weights.
- Impact (I): Computed from business criticality, MoSCoW tier, and core value drivers.
- Confidence (C): Computed from specification clarity, ambiguity penalty traces, and stakeholder linkage.
- Effort (E): Computed from functional complexity indicators or actual WBS task hours (hours / 160).
- RICE Score = (Reach * Impact * Confidence) / Effort
- Backlog Ranking: Deterministic descending sort by RICE score with rank assignment (#1, #2, ...).
"""

import logging
import re
from typing import Any, Dict, List, Optional

from app.schemas import (
    FunctionalRequirement,
    Priority,
    RICEScore,
    Stakeholder,
    Ambiguity,
    RequirementAnalysis,
    ProjectPlan
)

logger = logging.getLogger("software-blueprint-ai.rice")

DEFAULT_MONTHLY_USER_COHORT = 5000.0


def calculate_manual_reach(
    fr: FunctionalRequirement,
    stakeholders: List[Stakeholder],
    base_user_cohort: float = DEFAULT_MONTHLY_USER_COHORT
) -> float:
    """
    Manually calculate Reach (users/month affected by this feature).
    Evaluates linked stakeholder roles (Customer vs Staff vs Admin) and MoSCoW scope.
    """
    # Build stakeholder lookup by ID
    st_map = {st.id: st for st in stakeholders}
    linked_sts = [st_map[sid] for sid in fr.stakeholders if sid in st_map]

    # Stakeholder Scope Factor:
    # 1.0 = End-users / customers / public (100% of cohort)
    # 0.35 = Internal operators / specialists / drivers / doctors / managers (35% of cohort)
    # 0.08 = System administrators / IT / compliance officers (8% of cohort)
    max_scope_factor = 0.5  # default baseline if no stakeholders mapped

    if linked_sts:
        factors = []
        for st in linked_sts:
            name_desc = (st.name + " " + st.description).lower()
            if any(k in name_desc for k in ["admin", "compliance", "auditor", "security officer", "devops", "it"]):
                factors.append(0.08)
            elif any(k in name_desc for k in ["operator", "manager", "staff", "driver", "doctor", "nurse", "instructor", "dispatcher", "merchant"]):
                factors.append(0.35)
            else:
                factors.append(1.0)
        max_scope_factor = max(factors)
    else:
        # Check text heuristics
        lower_desc = (fr.title + " " + fr.description).lower()
        if "admin" in lower_desc:
            max_scope_factor = 0.08
        elif any(k in lower_desc for k in ["manager", "operator", "staff"]):
            max_scope_factor = 0.35
        else:
            max_scope_factor = 1.0

    # MoSCoW Multiplier
    moscow_multipliers = {
        Priority.MUST: 1.0,
        Priority.SHOULD: 0.75,
        Priority.COULD: 0.40,
        Priority.WONT: 0.15,
    }
    m_val = fr.priority if isinstance(fr.priority, Priority) else Priority(fr.priority)
    m_mult = moscow_multipliers.get(m_val, 0.75)

    computed_reach = round(base_user_cohort * max_scope_factor * m_mult, 0)
    return max(100.0, computed_reach)


def calculate_manual_impact(fr: FunctionalRequirement) -> float:
    """
    Manually calculate Impact (standardized scale: 3.0 Massive, 2.0 High, 1.0 Medium, 0.5 Low, 0.25 Minimal).
    Evaluates business value criticality, revenue/auth/data drivers, and MoSCoW tier.
    """
    m_val = fr.priority if isinstance(fr.priority, Priority) else Priority(fr.priority)
    text = (fr.title + " " + fr.description).lower()

    # Core business drivers trigger massive impact
    core_drivers = [
        "payment", "checkout", "transfer", "auth", "login", "register",
        "security", "prescri", "vital", "emergency", "order", "book"
    ]
    is_core = any(cd in text for cd in core_drivers)

    if m_val == Priority.MUST:
        return 3.0 if is_core else 2.0
    elif m_val == Priority.SHOULD:
        return 2.0 if is_core else 1.0
    elif m_val == Priority.COULD:
        return 0.5
    else:
        return 0.25


def calculate_manual_confidence(
    fr: FunctionalRequirement,
    ambiguities: List[Ambiguity]
) -> float:
    """
    Manually calculate Confidence (1.0 = 100% High, 0.8 = 80% Medium, 0.5 = 50% Low/Moonshot).
    Audits specification completeness, stakeholder bindings, and unclarified ambiguity overlaps.
    """
    score = 1.0
    text_lower = (fr.id + " " + fr.title + " " + fr.description).lower()

    # Check for ambiguity overlap
    for amb in ambiguities:
        amb_text = (amb.ambiguity + " " + amb.possible_clarification).lower()
        tokens = set(re.findall(r"\b[a-zA-Z]{4,}\b", amb_text))
        fr_tokens = set(re.findall(r"\b[a-zA-Z]{4,}\b", text_lower))
        overlap = tokens.intersection(fr_tokens)
        if len(overlap) >= 2 or fr.id.lower() in amb_text:
            score -= 0.30
            break

    # Penalty for missing stakeholder bindings
    if not fr.stakeholders:
        score -= 0.10

    # Penalty for short or vague descriptions
    if len(fr.description.strip()) < 40:
        score -= 0.10

    # Map to standardized confidence buckets
    if score >= 0.90:
        return 1.0  # 100% High
    elif score >= 0.70:
        return 0.8  # 80% Medium
    return 0.5      # 50% Moonshot / Low


def calculate_manual_effort(
    fr: FunctionalRequirement,
    tasks: Optional[List[Any]] = None
) -> float:
    """
    Manually calculate Effort in person-months (clamped >= 0.2 person-months).
    If WBS tasks are provided, computes actual engineering hours divided by 160 hrs/person-month.
    Otherwise, derives effort from functional scope complexity heuristics.
    """
    # Case 1: Compute from actual Work Breakdown Structure (WBS) engineering hours
    if tasks:
        linked_tasks = [t for t in tasks if hasattr(t, "requirement_ids") and fr.id in t.requirement_ids]
        if linked_tasks:
            total_hours = sum(getattr(t, "estimated_hours", 8.0) for t in linked_tasks)
            # 1 person-month = 160 hours (40 hours/week * 4 weeks)
            person_months = round(total_hours / 160.0, 2)
            return max(0.20, person_months)

    # Case 2: Derive from functional scope complexity
    text = (fr.title + " " + fr.description).lower()
    base_effort = 1.0

    high_complexity_indicators = [
        "encrypt", "biometric", "payment", "multi-factor", "real-time",
        "streaming", "telemetry", "firmware", "route optimization", "pci"
    ]
    if any(k in text for k in high_complexity_indicators):
        base_effort += 0.5

    # Integration points penalty
    if len(fr.stakeholders) > 1:
        base_effort += 0.2

    # Low complexity deductions
    if any(k in text for k in ["download", "export", "csv", "display", "notify", "email confirmation"]):
        base_effort -= 0.3

    return max(0.25, round(base_effort, 2))


def compute_manual_rice_score(
    fr: FunctionalRequirement,
    stakeholders: List[Stakeholder],
    ambiguities: List[Ambiguity],
    tasks: Optional[List[Any]] = None
) -> RICEScore:
    """
    Compute complete RICE score manually in pure Python code for a single requirement:
    RICE Score = (Reach * Impact * Confidence) / Effort
    """
    reach = calculate_manual_reach(fr, stakeholders)
    impact = calculate_manual_impact(fr)
    confidence = calculate_manual_confidence(fr, ambiguities)
    effort = calculate_manual_effort(fr, tasks)

    eff = max(0.1, effort)
    score = round((reach * impact * confidence) / eff, 2)

    return RICEScore(
        reach=reach,
        impact=impact,
        confidence=confidence,
        effort=effort,
        score=score,
        rank=None
    )


def apply_manual_rice_algorithm(
    analysis: RequirementAnalysis,
    project_plan: Optional[ProjectPlan] = None,
    force_recalculate: bool = False
) -> RequirementAnalysis:
    """
    Execute the RICE algorithm manually in code across all functional requirements:
    1. Computes Reach, Impact, Confidence, Effort, and Score for each FR using deterministic code.
    2. Sorts requirements descending by RICE Score.
    3. Assigns objective backlog ranks (Rank #1, #2, #3, ...).
    """
    if not analysis.functional_requirements:
        return analysis

    tasks = project_plan.tasks if project_plan else None

    # Step 1: Calculate RICE for every requirement manually in code
    for fr in analysis.functional_requirements:
        if fr.rice is None or force_recalculate:
            fr.rice = compute_manual_rice_score(
                fr=fr,
                stakeholders=analysis.stakeholders,
                ambiguities=analysis.ambiguities,
                tasks=tasks
            )
        elif tasks:
            # If tasks are provided from Module 2 (WBS), calibrate effort and score
            calibrated_effort = calculate_manual_effort(fr, tasks)
            fr.rice.effort = calibrated_effort
            eff = max(0.1, calibrated_effort)
            fr.rice.score = round((fr.rice.reach * fr.rice.impact * fr.rice.confidence) / eff, 2)

    # Step 2: Deterministic Backlog Ranking (sort descending by RICE score)
    # Tie-breaker: MoSCoW priority weight, then requirement ID
    priority_weights = {
        Priority.MUST: 4,
        Priority.SHOULD: 3,
        Priority.COULD: 2,
        Priority.WONT: 1
    }

    def sort_key(f: FunctionalRequirement):
        score_val = f.rice.score if f.rice else 0.0
        p_val = f.priority if isinstance(f.priority, Priority) else Priority(f.priority)
        p_weight = priority_weights.get(p_val, 2)
        return (score_val, p_weight, f.id)

    sorted_frs = sorted(analysis.functional_requirements, key=sort_key, reverse=True)

    # Step 3: Assign sequential 1-based ranks
    for rank_idx, s_fr in enumerate(sorted_frs, start=1):
        if s_fr.rice:
            s_fr.rice.rank = rank_idx

    # Maintain the sorted order in the analysis
    analysis.functional_requirements = sorted_frs
    return analysis
