"""Orchestrate routing, retrieval, grounded generation, and safe public metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from api.gemini_service import GeminiService
from api.intent_router import IntentRouter, normalize_text
from api.models import AskAmanResponse, ConversationExchange, PublicLink, SourceReference
from api.prompt import build_system_prompt
from api.retriever import HybridRetriever, QueryEmbeddingError, get_default_retriever


class InformationUnavailableError(RuntimeError):
    """The public portfolio does not have sufficiently relevant context."""


class RetrievalUnavailableError(RuntimeError):
    """Semantic retrieval cannot run because its query embedding is unavailable."""


@dataclass(frozen=True)
class SuggestionSet:
    items: tuple[str, ...]


SUGGESTIONS = {
    "about": SuggestionSet(("Where is Aman based?", "What opportunities is Aman open to?")),
    "education": SuggestionSet(("Where did Aman complete B.Tech?", "What subjects did Aman study?")),
    "skills": SuggestionSet(("What AI skills does Aman use?", "What web technologies does Aman work with?")),
    "projects": SuggestionSet(("Tell me about Poetic Pebbles.", "What projects has Aman built?")),
    "experience": SuggestionSet(("Where does Aman work?", "What does Aman do at GlobalLogic?")),
    "contact": SuggestionSet(("How can I contact Aman?", "Where can I find Aman's GitHub?")),
    "faq": SuggestionSet(("What projects has Aman built?", "What are Aman's AI skills?")),
    "general": SuggestionSet(("What projects has Aman built?", "What are Aman's AI skills?")),
}


class RAGService:
    """A transient, context-only service with no message persistence or logging."""

    def __init__(self, retriever: HybridRetriever, router: IntentRouter, generator: GeminiService) -> None:
        self._retriever = retriever
        self._router = router
        self._generator = generator

    def answer(self, question: str, history: Sequence[ConversationExchange]) -> AskAmanResponse:
        intent = self._router.route(question)
        if "external_link" in intent.actions:
            return self._deterministic_link_answer(question, intent.primary_intent)
        try:
            records = self._retriever.retrieve(question, intent)
        except QueryEmbeddingError as error:
            raise RetrievalUnavailableError("Ask Aman cannot search the portfolio right now. Please try again shortly.") from error
        if not records:
            raise InformationUnavailableError(
                "That information is not available in Aman's portfolio. Please use the Contact section for a direct question."
            )

        answer = self._generator.generate_answer(build_system_prompt(records), question, history[-2:])
        sources = [SourceReference(title=record.title, section=record.source_section) for record in records]
        suggestions = list(SUGGESTIONS.get(intent.primary_intent, SUGGESTIONS["general"]).items)
        return AskAmanResponse(answer=answer, sources=sources, suggestions=suggestions, intent=intent.primary_intent)

    def _deterministic_link_answer(self, question: str, primary_intent: str) -> AskAmanResponse:
        """Return only validated knowledge links; never ask Gemini to create a URL."""

        normalized_question = normalize_text(question)
        for record in self._retriever.knowledge_records:
            if record.category != "projects" or not record.links:
                continue
            project_name = normalize_text(record.title.removesuffix(" overview"))
            if not project_name or not f" {project_name} " in f" {normalized_question} ":
                continue
            link = record.links[0]
            answer = (
                "You can download Poetic Pebbles directly from Google Play."
                if link.type == "play_store" and project_name == "poetic pebbles"
                else f"You can access {record.title.removesuffix(' overview')} using the verified public link below."
            )
            return AskAmanResponse(
                answer=answer,
                sources=[SourceReference(title=record.title, section=record.source_section)],
                links=[PublicLink.model_validate(link)],
                suggestions=list(SUGGESTIONS["projects"].items),
                intent="projects",
            )

        return AskAmanResponse(
            answer="A verified public link for this project is not currently available in Aman's portfolio.",
            sources=[],
            links=[],
            suggestions=list(SUGGESTIONS.get(primary_intent, SUGGESTIONS["projects"]).items),
            intent=primary_intent,
        )


_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    """Construct the process-local service lazily so health never calls Gemini."""

    global _rag_service
    if _rag_service is None:
        retriever = get_default_retriever()
        _rag_service = RAGService(retriever, IntentRouter(retriever.knowledge_records), GeminiService())
    return _rag_service
