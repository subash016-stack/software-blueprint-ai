"""Centralized configuration and environment settings for Software Blueprint AI."""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment or .env."""

    # Ollama LLM Configuration
    ollama_base_url: str = "http://localhost:11434"
    generation_model: str = "qwen3:4b"
    fallback_generation_model: str = "qwen2.5:3b"
    embedding_model: str = "qwen3-embedding:0.6b"
    fallback_embedding_model: str = "nomic-embed-text"
    ollama_temperature: float = 0.0

    # Cache Configuration
    redis_url: str = "redis://localhost:6379"
    enable_redis: bool = True
    cache_ttl_seconds: int = 86400  # 24 hours

    # Vector Store Configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "software_engineering_knowledge"
    qdrant_api_key: str = ""

    # Database Configuration
    database_url: str = "sqlite:///./software_blueprint.db"

    # Prompt Versions (for cache key invalidation and reproducibility)
    requirement_prompt_version: str = "1.0"
    planning_prompt_version: str = "1.0"
    architecture_prompt_version: str = "1.0"
    rag_prompt_version: str = "1.0"
    validation_prompt_version: str = "1.0"
    impact_prompt_version: str = "1.0"

    # Schema Version
    schema_version: str = "1.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Return singleton cached application settings instance."""
    return Settings()
