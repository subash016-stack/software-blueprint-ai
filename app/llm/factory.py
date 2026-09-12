"""Centralized LLM factory, resilient structured JSON invocation, and observability tracking."""

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Type, TypeVar
from langchain_ollama import ChatOllama
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger("software-blueprint-ai.llm")

T = TypeVar("T", bound=BaseModel)


class MetricsTracker:
    """In-memory observability metrics tracker for LLM and Cache performance."""
    total_llm_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    input_tokens_estimated: int = 0
    output_tokens_estimated: int = 0
    estimated_tokens_saved: int = 0
    total_latency_ms: float = 0.0
    llm_latencies: List[float] = []

    @classmethod
    def record_llm_call(cls, latency_ms: float, input_chars: int = 0, output_chars: int = 0):
        cls.total_llm_calls += 1
        cls.total_latency_ms += latency_ms
        cls.llm_latencies.append(latency_ms)
        # Approximate 4 chars per token for rough token metric tracking
        in_tokens = max(1, input_chars // 4)
        out_tokens = max(1, output_chars // 4)
        cls.input_tokens_estimated += in_tokens
        cls.output_tokens_estimated += out_tokens

    @classmethod
    def record_cache_hit(cls, saved_chars: int = 2000):
        cls.cache_hits += 1
        cls.estimated_tokens_saved += max(100, saved_chars // 4)

    @classmethod
    def record_cache_miss(cls):
        cls.cache_misses += 1

    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        total_requests = cls.cache_hits + cls.cache_misses
        hit_rate = (cls.cache_hits / total_requests * 100.0) if total_requests > 0 else 0.0
        avg_latency = (cls.total_latency_ms / cls.total_llm_calls) if cls.total_llm_calls > 0 else 0.0
        return {
            "total_llm_calls": cls.total_llm_calls,
            "cache_hits": cls.cache_hits,
            "cache_misses": cls.cache_misses,
            "cache_hit_rate_percent": round(hit_rate, 2),
            "estimated_input_tokens": cls.input_tokens_estimated,
            "estimated_output_tokens": cls.output_tokens_estimated,
            "estimated_tokens_saved": cls.estimated_tokens_saved,
            "average_llm_latency_ms": round(avg_latency, 2),
        }

    @classmethod
    def reset(cls):
        cls.total_llm_calls = 0
        cls.cache_hits = 0
        cls.cache_misses = 0
        cls.input_tokens_estimated = 0
        cls.output_tokens_estimated = 0
        cls.estimated_tokens_saved = 0
        cls.total_latency_ms = 0.0
        cls.llm_latencies = []


def get_llm(
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    format: str = "json"
) -> ChatOllama:
    """Create and return an optimized ChatOllama instance fit for 4GB VRAM GPU acceleration."""
    settings = get_settings()
    target_model = model or settings.generation_model
    temp = settings.ollama_temperature if temperature is None else temperature

    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=target_model,
        temperature=temp,
        format=format,
        num_ctx=2048,
        num_predict=1024,
        num_thread=8,
        timeout=180.0,
    )


def _camel_to_snake(name: str) -> str:
    """Convert camelCase string to snake_case."""
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def _normalize_keys(obj: Any) -> Any:
    """Recursively normalize dictionary keys from camelCase to snake_case."""
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            snake_k = _camel_to_snake(k) if isinstance(k, str) else k
            new_dict[snake_k] = _normalize_keys(v)
        return new_dict
    elif isinstance(obj, list):
        return [_normalize_keys(item) for item in obj]
    return obj


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract and parse JSON object from raw LLM output with fuzzy repairs and key normalization."""
    if not text or not text.strip():
        raise ValueError("Empty response received from LLM.")

    # 1. Strip markdown code fences if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    candidate = match.group(1).strip() if match else text.strip()

    # 2. Try to find the outermost matching braces { ... }
    brace_match = re.search(r"(\{[\s\S]*\})", candidate)
    if brace_match:
        candidate = brace_match.group(1)

    # 3. Direct parse
    parsed_data = None
    try:
        parsed_data = json.loads(candidate)
    except json.JSONDecodeError:
        # 4. Repair trailing commas and common JSON flaws
        cleaned = re.sub(r",\s*([\]}])", r"\1", candidate)
        cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", cleaned)  # Strip unescaped control chars
        try:
            parsed_data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning("Fuzzy JSON parse failed: %s. Raw candidate: %s", e, candidate[:200])
            raise ValueError(f"Failed to parse valid JSON from LLM response: {e}")

    if isinstance(parsed_data, dict):
        return _normalize_keys(parsed_data)
    elif isinstance(parsed_data, list):
        return _normalize_keys(parsed_data)
    return parsed_data


def invoke_structured(
    prompt_messages: list,
    schema: Type[T],
    temperature: float = 0.0,
    model_override: Optional[str] = None
) -> T:
    """Invoke Ollama LLM and return validated Pydantic model with retry fallback."""
    settings = get_settings()
    models_to_try = [model_override or settings.generation_model]
    if settings.fallback_generation_model and settings.fallback_generation_model not in models_to_try:
        models_to_try.append(settings.fallback_generation_model)

    start_time = time.time()
    input_chars = sum(len(getattr(m, "content", str(m))) for m in prompt_messages)

    last_error = None
    for model_name in models_to_try:
        try:
            llm = get_llm(model=model_name, temperature=temperature, format="json")
            response = llm.invoke(prompt_messages)
            raw_content = response.content if hasattr(response, "content") else str(response)
            output_chars = len(raw_content)

            latency_ms = (time.time() - start_time) * 1000.0
            MetricsTracker.record_llm_call(latency_ms, input_chars, output_chars)

            data = extract_json_from_text(raw_content)
            return schema.model_validate(data)
        except Exception as e:
            logger.warning("Structured invocation failed with model %s: %s", model_name, e)
            last_error = e

    # Fallback to with_structured_output method
    try:
        raw_llm = get_llm(model=models_to_try[0], temperature=temperature, format="")
        structured_llm = raw_llm.with_structured_output(schema)
        result = structured_llm.invoke(prompt_messages)
        latency_ms = (time.time() - start_time) * 1000.0
        MetricsTracker.record_llm_call(latency_ms, input_chars, 500)
        if isinstance(result, schema):
            return result
        return schema.model_validate(result)
    except Exception as e:
        logger.error("All structured invocation attempts failed: %s", e)
        raise last_error or e
