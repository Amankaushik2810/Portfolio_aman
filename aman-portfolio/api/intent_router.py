"""Deterministic intent routing for Ask Aman without an LLM dependency."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from api.models import KnowledgeRecord


SUPPORTED_INTENTS = (
    "about",
    "education",
    "skills",
    "projects",
    "experience",
    "contact",
    "faq",
    "general",
)
CONTENT_INTENTS = SUPPORTED_INTENTS[:-1]


@dataclass(frozen=True)
class IntentSignals:
    """Configurable normalized terms for one intent category."""

    keywords: tuple[str, ...] = ()
    phrases: tuple[str, ...] = ()
    entities: tuple[str, ...] = ()


@dataclass(frozen=True)
class IntentResult:
    """The ranked route for a visitor question."""

    primary_intent: str
    related_intents: tuple[str, ...]
    confidence: float
    matched_terms: tuple[str, ...]
    actions: tuple[str, ...] = ()


# Extend this mapping rather than changing routing logic when new portfolio content is added.
DEFAULT_INTENT_SIGNALS: dict[str, IntentSignals] = {
    "about": IntentSignals(
        keywords=("background", "hometown", "based", "from", "availability", "opportunities"),
        phrases=("tell me about aman", "about aman", "who is aman", "where is aman from"),
    ),
    "education": IntentSignals(
        keywords=("education", "degree", "university", "college", "school", "b tech", "cbse", "pcm", "lpu"),
        phrases=("where did aman study", "where did aman complete b tech", "education background"),
    ),
    "skills": IntentSignals(
        keywords=("skills", "skill", "technology", "technologies", "ai", "machine learning", "ml", "nlp", "rag", "llms"),
        phrases=("what can aman do", "technical skills", "ai skills", "machine learning skills"),
    ),
    "projects": IntentSignals(
        keywords=("project", "projects", "built", "portfolio", "application", "app"),
        phrases=("tell me about the project", "what has aman built", "show me projects"),
    ),
    "experience": IntentSignals(
        keywords=("work", "works", "working", "company", "job", "role", "employer", "career"),
        phrases=("where does aman work", "what is aman current role", "work experience"),
    ),
    "contact": IntentSignals(
        keywords=("contact", "email", "linkedin", "github", "reach", "connect"),
        phrases=("how can i contact aman", "how do i contact aman", "reach aman", "get in touch"),
    ),
    "faq": IntentSignals(
        keywords=("help",),
        phrases=("what can i ask", "what can you answer", "how can you help", "help me"),
    ),
}

GREETING_PHRASES = ("hello", "hi", "hey", "good morning", "good afternoon", "good evening")
BROAD_QUESTION_PHRASES = ("tell me everything", "everything about aman", "all about aman", "tell me all about aman")
LINK_REQUEST_PHRASES = (
    "share the link",
    "share me the link",
    "give me the link",
    "app link",
    "play store link",
    "download",
    "install",
    "where can i get it",
    "where is the app available",
    "google play",
)


def normalize_text(value: str) -> str:
    """Lowercase and normalize punctuation so phrase matching is predictable."""

    normalized = unicodedata.normalize("NFKD", value).lower()
    normalized = "".join(character for character in normalized if not unicodedata.combining(character))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", normalized)).strip()


def _contains_term(question: str, term: str) -> bool:
    return f" {term} " in f" {question} "


def _without_suffix(value: str, suffix: str) -> str:
    return re.sub(rf"\s+{suffix}$", "", value, flags=re.IGNORECASE).strip()


def _knowledge_entities(records: Iterable[KnowledgeRecord]) -> dict[str, set[str]]:
    """Extract stable project and employer names from the public knowledge records."""

    entities = {"projects": set(), "experience": set()}
    for record in records:
        if record.category == "projects" and record.id.endswith("-overview"):
            entities["projects"].add(_without_suffix(record.title, "overview"))
        elif record.category == "experience" and record.id.endswith("-role"):
            entities["experience"].add(record.title.rsplit(" at ", maxsplit=1)[-1])
            employer_match = re.search(r"at ([^,]+), a ([^.]+) company", record.content, re.IGNORECASE)
            if employer_match:
                entities["experience"].update(employer_match.groups())
    return entities


class IntentRouter:
    """Score every supported content intent using deterministic configurable signals."""

    def __init__(
        self,
        records: Iterable[KnowledgeRecord] = (),
        signal_overrides: Mapping[str, IntentSignals] | None = None,
    ) -> None:
        self._signals = {intent: signals for intent, signals in DEFAULT_INTENT_SIGNALS.items()}
        if signal_overrides:
            invalid_intents = set(signal_overrides) - set(CONTENT_INTENTS)
            if invalid_intents:
                raise ValueError(f"Unsupported intent overrides: {', '.join(sorted(invalid_intents))}")
            self._signals.update(signal_overrides)

        derived_entities = _knowledge_entities(records)
        for intent, entities in derived_entities.items():
            existing = self._signals[intent]
            self._signals[intent] = IntentSignals(
                keywords=existing.keywords,
                phrases=existing.phrases,
                entities=tuple((*existing.entities, *sorted(entities))),
            )

    def route(self, question: str) -> IntentResult:
        normalized_question = normalize_text(question)
        if not normalized_question:
            return IntentResult("general", (), 0.0, ())

        if any(_contains_term(normalized_question, phrase) for phrase in BROAD_QUESTION_PHRASES):
            return IntentResult("general", CONTENT_INTENTS, 0.2, ("broad question",))

        matched_link_phrase = next(
            (phrase for phrase in LINK_REQUEST_PHRASES if _contains_term(normalized_question, phrase)),
            None,
        )

        scores: dict[str, int] = {intent: 0 for intent in CONTENT_INTENTS}
        matched_by_intent: dict[str, list[str]] = {intent: [] for intent in CONTENT_INTENTS}
        for intent, signals in self._signals.items():
            self._score_terms(normalized_question, signals.keywords, 2, scores, matched_by_intent, intent)
            self._score_terms(normalized_question, signals.phrases, 4, scores, matched_by_intent, intent)
            self._score_terms(normalized_question, signals.entities, 6, scores, matched_by_intent, intent)

        ranked = sorted(
            ((intent, score) for intent, score in scores.items() if score),
            key=lambda item: (-item[1], CONTENT_INTENTS.index(item[0])),
        )
        if not ranked:
            greeting = next((phrase for phrase in GREETING_PHRASES if _contains_term(normalized_question, phrase)), None)
            return IntentResult(
                "general",
                (),
                0.95 if greeting else 0.2,
                (greeting,) if greeting else (),
                ("external_link",) if matched_link_phrase else (),
            )

        primary_intent, primary_score = ranked[0]
        related_intents = tuple(
            intent
            for intent, score in ranked[1:]
            if score >= max(2, primary_score * 0.3)
        )
        matched_terms = tuple(
            term
            for intent, _ in ranked
            for term in matched_by_intent[intent]
        )
        confidence = round(min(0.98, 0.45 + primary_score * 0.07), 2)
        actions = ("external_link",) if matched_link_phrase else ()
        if matched_link_phrase:
            matched_terms = (*matched_terms, matched_link_phrase)
        return IntentResult(primary_intent, related_intents, confidence, matched_terms, actions)

    @staticmethod
    def _score_terms(
        question: str,
        raw_terms: Sequence[str],
        weight: int,
        scores: dict[str, int],
        matched_by_intent: dict[str, list[str]],
        intent: str,
    ) -> None:
        for raw_term in raw_terms:
            term = normalize_text(raw_term)
            if term and _contains_term(question, term) and term not in matched_by_intent[intent]:
                scores[intent] += weight
                matched_by_intent[intent].append(term)
