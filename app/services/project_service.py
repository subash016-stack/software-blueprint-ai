"""Project and Blueprint version persistence service."""

import logging
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.schemas import (
    CompleteBlueprint,
    RequirementAnalysis,
    ProjectPlan,
    ArchitectureBlueprint,
    ValidationReport,
    GroundedRecommendation,
    BlueprintVersionSummary
)
from app.db.session import SessionLocal
from app.db.models import ProjectRecord, BlueprintVersionRecord

logger = logging.getLogger("software-blueprint-ai.projects")

# In-memory fast store for active projects
_ACTIVE_PROJECTS: Dict[str, CompleteBlueprint] = {}


def save_complete_blueprint(blueprint: CompleteBlueprint) -> CompleteBlueprint:
    """Save or update a complete blueprint in active memory and database."""
    _ACTIVE_PROJECTS[blueprint.project_id] = blueprint

    try:
        with SessionLocal() as db:
            project = db.query(ProjectRecord).filter(ProjectRecord.id == blueprint.project_id).first()
            if not project:
                project = ProjectRecord(
                    id=blueprint.project_id,
                    name=blueprint.project_name,
                    description=blueprint.requirements.project_description,
                    latest_version=blueprint.version
                )
                db.add(project)
            else:
                project.name = blueprint.project_name
                project.latest_version = blueprint.version
                project.updated_at = datetime.utcnow()

            version_record = BlueprintVersionRecord(
                id=f"{blueprint.project_id}-v{blueprint.version}",
                project_id=blueprint.project_id,
                version=blueprint.version,
                requirements_data=blueprint.requirements.model_dump(),
                project_plan_data=blueprint.project_plan.model_dump(),
                architecture_data=blueprint.architecture.model_dump(),
                rag_recommendations_data=[r.model_dump() for r in blueprint.rag_recommendations],
                validation_report_data=blueprint.validation_report.model_dump() if blueprint.validation_report else None,
                requirements_hash=blueprint.requirements.compute_hash(),
                plan_hash=blueprint.project_plan.compute_hash(),
                architecture_hash=blueprint.architecture.compute_hash(),
                quality_score=blueprint.validation_report.overall_score if blueprint.validation_report else 90,
                change_summary=f"Version {blueprint.version} Generated"
            )
            db.merge(version_record)
            db.commit()
    except Exception as e:
        logger.warning("Database persistence error (%s). Kept safely in memory.", e)

    return blueprint


def get_complete_blueprint(project_id: str) -> Optional[CompleteBlueprint]:
    """Retrieve complete blueprint by project ID."""
    if project_id in _ACTIVE_PROJECTS:
        return _ACTIVE_PROJECTS[project_id]

    try:
        with SessionLocal() as db:
            project = db.query(ProjectRecord).filter(ProjectRecord.id == project_id).first()
            if not project:
                return None

            latest_v = db.query(BlueprintVersionRecord).filter(
                BlueprintVersionRecord.project_id == project_id,
                BlueprintVersionRecord.version == project.latest_version
            ).first()

            if not latest_v:
                return None

            reqs = RequirementAnalysis.model_validate(latest_v.requirements_data)
            plan = ProjectPlan.model_validate(latest_v.project_plan_data)
            arch = ArchitectureBlueprint.model_validate(latest_v.architecture_data)
            rag = [GroundedRecommendation.model_validate(r) for r in (latest_v.rag_recommendations_data or [])]
            val = ValidationReport.model_validate(latest_v.validation_report_data) if latest_v.validation_report_data else None

            # Get version summaries
            all_versions = db.query(BlueprintVersionRecord).filter(
                BlueprintVersionRecord.project_id == project_id
            ).order_by(BlueprintVersionRecord.version.asc()).all()

            history = [
                BlueprintVersionSummary(
                    version=v.version,
                    created_at=v.created_at.isoformat() if v.created_at else datetime.utcnow().isoformat(),
                    requirements_hash=v.requirements_hash or "",
                    plan_hash=v.plan_hash or "",
                    architecture_hash=v.architecture_hash or "",
                    quality_score=v.quality_score,
                    change_summary=v.change_summary
                )
                for v in all_versions
            ]

            bp = CompleteBlueprint(
                project_id=project.id,
                project_name=project.name,
                version=project.latest_version,
                requirements=reqs,
                project_plan=plan,
                architecture=arch,
                rag_recommendations=rag,
                validation_report=val,
                version_history=history
            )
            _ACTIVE_PROJECTS[project_id] = bp
            return bp
    except Exception as e:
        logger.warning("Database read error (%s).", e)
        return None


def list_projects() -> List[Dict[str, Any]]:
    """List all available projects from active memory and database."""
    projects_dict = {}

    try:
        with SessionLocal() as db:
            db_projects = db.query(ProjectRecord).order_by(ProjectRecord.created_at.desc()).all()
            for p in db_projects:
                projects_dict[p.id] = {
                    "id": p.id,
                    "project_id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "version": p.latest_version,
                    "quality_score": 90
                }
    except Exception as e:
        logger.warning("Database list_projects error (%s).", e)

    for pid, bp in _ACTIVE_PROJECTS.items():
        projects_dict[pid] = {
            "id": pid,
            "project_id": pid,
            "name": bp.project_name,
            "description": bp.requirements.project_description,
            "version": bp.version,
            "quality_score": bp.validation_report.overall_score if bp.validation_report else 90
        }

    return list(projects_dict.values())
