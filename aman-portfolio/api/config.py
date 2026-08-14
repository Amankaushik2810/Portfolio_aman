"""Server-only environment configuration for the Ask Aman API."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_GENERATION_MODEL = "gemini-3.1-flash-lite"
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"
PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent


def _optional_environment_value(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


@dataclass(frozen=True)
class Settings:
    """Configuration loaded exclusively in the Python runtime."""

    gemini_api_key: str | None = field(repr=False)
    gemini_generation_model: str = DEFAULT_GENERATION_MODEL
    gemini_embedding_model: str = DEFAULT_EMBEDDING_MODEL

    @property
    def gemini_api_key_configured(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def generation_model_configured(self) -> bool:
        return bool(self.gemini_generation_model)

    @property
    def embedding_model_configured(self) -> bool:
        return bool(self.gemini_embedding_model)


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
    )


settings = load_settings()
