"""Server-only environment configuration for the Ask Aman API."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_GENERATION_MODEL = "gemini-3.1-flash-lite"
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"
DEFAULT_GEMINI_TIMEOUT_SECONDS = 20
DEFAULT_MAX_QUESTION_LENGTH = 300
DEFAULT_MAX_REQUEST_BODY_BYTES = 16 * 1024
DEFAULT_RATE_LIMIT = 8
DEFAULT_RATE_WINDOW_SECONDS = 60
DEFAULT_APP_ENVIRONMENT = "development"
PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent


def _optional_environment_value(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


def _bounded_environment_integer(name: str, default: int, minimum: int, maximum: int) -> int:
    value = _optional_environment_value(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return min(max(parsed, minimum), maximum)


@dataclass(frozen=True)
class Settings:
    """Configuration loaded exclusively in the Python runtime."""

    gemini_api_key: str | None = field(repr=False)
    gemini_generation_model: str = DEFAULT_GENERATION_MODEL
    gemini_embedding_model: str = DEFAULT_EMBEDDING_MODEL
    gemini_timeout_seconds: int = DEFAULT_GEMINI_TIMEOUT_SECONDS
    max_question_length: int = DEFAULT_MAX_QUESTION_LENGTH
    max_request_body_bytes: int = DEFAULT_MAX_REQUEST_BODY_BYTES
    rate_limit: int = DEFAULT_RATE_LIMIT
    rate_window_seconds: int = DEFAULT_RATE_WINDOW_SECONDS
    app_environment: str = DEFAULT_APP_ENVIRONMENT

    @property
    def gemini_api_key_configured(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def generation_model_configured(self) -> bool:
        return bool(self.gemini_generation_model)

    @property
    def embedding_model_configured(self) -> bool:
        return bool(self.gemini_embedding_model)

    @property
    def is_production(self) -> bool:
        return self.app_environment == "production" or os.getenv("VERCEL_ENV") == "production"


def load_settings() -> Settings:
    """Load local development variables without overriding Vercel environment values."""

    # Vercel supplies environment variables directly. Locally, allow ignored files
    # while keeping process variables authoritative and never loading the template.
    load_dotenv(PROJECT_DIRECTORY / ".env.local", override=False)
    load_dotenv(PROJECT_DIRECTORY / ".env", override=False)
    return Settings(
        gemini_api_key=_optional_environment_value("GEMINI_API_KEY"),
        gemini_generation_model=(
            _optional_environment_value("GEMINI_GENERATION_MODEL")
            or DEFAULT_GENERATION_MODEL
        ),
        gemini_embedding_model=(
            _optional_environment_value("GEMINI_EMBEDDING_MODEL")
            or DEFAULT_EMBEDDING_MODEL
        ),
        gemini_timeout_seconds=_bounded_environment_integer(
            "GEMINI_TIMEOUT_SECONDS", DEFAULT_GEMINI_TIMEOUT_SECONDS, 1, 55
        ),
        max_question_length=_bounded_environment_integer(
            "ASK_AMAN_MAX_QUESTION_LENGTH", DEFAULT_MAX_QUESTION_LENGTH, 1, 1_000
        ),
        max_request_body_bytes=_bounded_environment_integer(
            "ASK_AMAN_MAX_REQUEST_BODY_BYTES", DEFAULT_MAX_REQUEST_BODY_BYTES, 1_024, 65_536
        ),
        rate_limit=_bounded_environment_integer("ASK_AMAN_RATE_LIMIT", DEFAULT_RATE_LIMIT, 1, 100),
        rate_window_seconds=_bounded_environment_integer(
            "ASK_AMAN_RATE_WINDOW_SECONDS", DEFAULT_RATE_WINDOW_SECONDS, 1, 3_600
        ),
        app_environment=(_optional_environment_value("APP_ENV") or DEFAULT_APP_ENVIRONMENT).casefold(),
    )


settings = load_settings()
