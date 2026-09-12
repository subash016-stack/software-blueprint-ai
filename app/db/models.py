"""SQLAlchemy ORM models for Blueprint AI persistence."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class ProjectRecord(Base):
    """Database model for an engineering project."""
    __tablename__ = "projects"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    latest_version = Column(Integer, default=1)

    versions = relationship("BlueprintVersionRecord", back_populates="project", cascade="all, delete-orphan")


class BlueprintVersionRecord(Base):
    """Database model for immutable blueprint versions."""
    __tablename__ = "blueprint_versions"

    id = Column(String(64), primary_key=True, index=True)
    project_id = Column(String(64), ForeignKey("projects.id"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requirements_data = Column(JSON, nullable=False)
    project_plan_data = Column(JSON, nullable=False)
    architecture_data = Column(JSON, nullable=False)
    rag_recommendations_data = Column(JSON, nullable=True)
    validation_report_data = Column(JSON, nullable=True)
    
    requirements_hash = Column(String(64), nullable=True)
    plan_hash = Column(String(64), nullable=True)
    architecture_hash = Column(String(64), nullable=True)
    quality_score = Column(Integer, default=90)
    change_summary = Column(Text, nullable=True)

    project = relationship("ProjectRecord", back_populates="versions")
