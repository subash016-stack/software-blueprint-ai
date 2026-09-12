"""Backwards-compatible wrapper exposing LLM factory functions and settings."""

from app.config import get_settings, Settings
from app.llm.factory import (
    get_llm,
    invoke_structured,
    extract_json_from_text,
    MetricsTracker
)

__all__ = [
    "get_settings",
    "Settings",
    "get_llm",
    "invoke_structured",
    "extract_json_from_text",
    "MetricsTracker"
]
