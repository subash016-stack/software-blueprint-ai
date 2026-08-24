"""Ollama LLM client configuration and resilient structured output invocation."""

import json
import re
from functools import lru_cache
from typing import Any, Dict, Type, TypeVar
from langchain_ollama import ChatOllama
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

T = TypeVar("T", bound=BaseModel)


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables or .env."""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    ollama_temperature: float = 0.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


def get_llm(temperature: float = None, format: str = "json") -> ChatOllama:
    """Create and return a ChatOllama instance configured with current settings."""
    settings = get_settings()
    temp = settings.ollama_temperature if temperature is None else temperature
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=temp,
        format=format,
    )


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract and parse JSON object from text that may contain markdown or surrounding text."""
    # Strip markdown code fences if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    candidate = match.group(1) if match else text

    # Try to find the outermost matching braces { ... }
    brace_match = re.search(r"(\{[\s\S]*\})", candidate)
    if brace_match:
        candidate = brace_match.group(1)

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Try removing trailing commas
        cleaned = re.sub(r",\s*([\]}])", r"\1", candidate)
        return json.loads(cleaned)


def invoke_structured(
    prompt_messages: list,
    schema: Type[T],
    temperature: float = 0.0
) -> T:
    """Invoke Ollama LLM and return validated Pydantic model.
    
    Uses Ollama's native JSON mode with Pydantic validation and resilient fallback.
    """
    llm = get_llm(temperature=temperature, format="json")
    
    # 1. Native JSON invocation
    try:
        response = llm.invoke(prompt_messages)
        raw_content = response.content if hasattr(response, "content") else str(response)
        data = extract_json_from_text(raw_content)
        return schema.model_validate(data)
    except Exception:
        pass

    # 2. Fallback attempt: with_structured_output
    raw_llm = get_llm(temperature=temperature, format="")
    structured_llm = raw_llm.with_structured_output(schema)
    result = structured_llm.invoke(prompt_messages)
    if isinstance(result, schema):
        return result
    return schema.model_validate(result)

