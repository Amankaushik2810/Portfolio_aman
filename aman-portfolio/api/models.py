"""Pydantic models shared by the Ask Aman API and knowledge loader."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from api.link_validation import public_link_error


KnowledgeCategory = Literal[
    "about",
    "education",
    "skills",
    "projects",
    "experience",
    "contact",
    "faq",
]


class PublicLink(BaseModel):
    """A verified portfolio link that is never supplied by an LLM or visitor."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    url: str = Field(min_length=1)
    type: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_public_link(self) -> "PublicLink":
        error = public_link_error(self.id, self.label, self.url, self.type)
        if error:
            raise ValueError(error)
        return self


class KnowledgeRecord(BaseModel):
    """One retrieval-ready record from the public portfolio knowledge base."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(min_length=1)
    category: KnowledgeCategory
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    keywords: list[str] = Field(min_length=1)
    source_section: KnowledgeCategory
    links: list[PublicLink] = Field(default_factory=list)


class AskAmanRequest(BaseModel):
    """Bounded request shape for the public Ask Aman endpoint."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    question: str = Field(min_length=1, max_length=300)
    history: list["ConversationExchange"] = Field(default_factory=list, max_length=2)


class ConversationExchange(BaseModel):
    """A recent transient exchange supplied by the visitor; never persisted by the API."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    question: str = Field(min_length=1, max_length=300)
    answer: str = Field(min_length=1, max_length=1200)


AskAmanRequest.model_rebuild()


class SourceReference(BaseModel):
    title: str
    section: KnowledgeCategory


class AskAmanResponse(BaseModel):
    """Public grounded answer without internal prompt, vector, or configuration data."""

    answer: str
    sources: list[SourceReference] = Field(default_factory=list)
    links: list[PublicLink] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list, max_length=3)
    intent: str


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class KnowledgeHealth(BaseModel):
    loaded: bool
    record_count: int
    categories: dict[str, int] = Field(default_factory=dict)
    error: str | None = None


class ConfigurationHealth(BaseModel):
    gemini_api_key_configured: bool
    generation_model_configured: bool
    embedding_model_configured: bool
    generation_model: str
    embedding_model: str


class IndexHealth(BaseModel):
    loaded: bool
    record_count: int
    embedding_dimension: int | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    knowledge: KnowledgeHealth
    index: IndexHealth
    configuration: ConfigurationHealth
