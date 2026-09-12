"""Database persistence module."""

from app.db.session import Base, engine, SessionLocal, get_db
from app.db.models import ProjectRecord, BlueprintVersionRecord

# Automatically create tables if not existing
Base.metadata.create_all(bind=engine)

__all__ = ["Base", "engine", "SessionLocal", "get_db", "ProjectRecord", "BlueprintVersionRecord"]
