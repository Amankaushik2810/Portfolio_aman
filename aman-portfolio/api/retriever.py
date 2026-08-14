"""Hybrid semantic retrieval for Ask Aman without exposing document vectors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np
from google import genai
from google.genai import types

from api.config import settings
from api.data_loader import KnowledgeBase, load_knowledge_base
from api.intent_router import IntentResult
from scripts.build_index import (
    INDEX_PATH,
    QUERY_TASK_TYPE,
    IndexValidationError,
    _read_index,
    validate_index,
)


class RetrievalInitializationError(RuntimeError):
    """Raised when the persisted vector index is unavailable or stale."""


class QueryEmbeddingError(RuntimeError):
    """Raised when a compatible query embedding cannot be generated."""


@dataclass(frozen=True)
class RetrievalConfig:
    max_results: int = 3
    relevance_threshold: float = 0.28
    primary_intent_boost: float = 0.06
    related_intent_boost: float = 0.03
    intent_fallback_confidence: float = 0.8


@dataclass(frozen=True)
class RetrievedRecord:
    record_id: str
    title: str
    category: str
    source_section: str
    content: str
    semantic_score: float
    applied_intent_boost: float
    final_score: float


QueryEmbedder = Callable[[str], Iterable[float]]


class HybridRetriever:
    """Rank global semantic matches and apply only small intent-aware boosts."""

    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        index: dict,
        query_embedder: QueryEmbedder | None = None,
        config: RetrievalConfig = RetrievalConfig(),
    ) -> None:
        try:
            self._dimension = validate_index(index, knowledge_base)
        except IndexValidationError as error:
            raise RetrievalInitializationError(f"Ask Aman vector index is invalid or stale: {error}") from error

        self._knowledge_by_id = {record.id: record for record in knowledge_base.records}
        self._model = index["embedding_model"]
        self._query_task_type = index["query_task_type"]
        self._config = config
        self._query_embedder = query_embedder
        self._client: genai.Client | None = None

        index_vectors = {entry["record_id"]: entry["embedding"] for entry in index["vectors"]}
        ordered_ids = tuple(record.id for record in knowledge_base.records)
        self._record_ids = ordered_ids
        matrix = np.asarray([index_vectors[record_id] for record_id in ordered_ids], dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1)
        self._normalized_document_vectors = np.divide(
            matrix,
            norms[:, np.newaxis],
            out=np.zeros_like(matrix),
            where=norms[:, np.newaxis] != 0,
        )

    @property
    def knowledge_records(self):
        """Expose validated source records without exposing private vector data."""

        return tuple(self._knowledge_by_id.values())

    @property
    def indexed_record_count(self) -> int:
        """Return index coverage without exposing vector contents."""

        return len(self._record_ids)

    @property
    def embedding_dimension(self) -> int:
        """Return the validated document/query vector dimension."""

        return self._dimension

    def retrieve(self, question: str, intent: IntentResult) -> list[RetrievedRecord]:
        """Generate one query embedding and return up to three hybrid-ranked records."""

        query_vector = self._normalized_query_vector(question)
        semantic_scores = self._normalized_document_vectors @ query_vector
        relevant_intents = {intent.primary_intent, *intent.related_intents} - {"general"}

        global_candidates: list[RetrievedRecord] = []
        intent_candidates: list[RetrievedRecord] = []
        for record_id, semantic_score in zip(self._record_ids, semantic_scores, strict=True):
            semantic_score = float(semantic_score)
            if semantic_score < self._config.relevance_threshold:
                continue
            record = self._knowledge_by_id[record_id]
            boost = self._intent_boost(record.category, intent)
            candidate = RetrievedRecord(
                record_id=record.id,
                title=record.title,
                category=record.category,
                source_section=record.source_section,
                content=record.content,
                semantic_score=round(semantic_score, 6),
                applied_intent_boost=round(boost, 6),
                final_score=round(semantic_score + boost, 6),
            )
            global_candidates.append(candidate)
            if record.category in relevant_intents:
                intent_candidates.append(candidate)

        # Category-aware and global candidate sets intentionally overlap. Merging by
        # ID preserves intent benefits without excluding cross-category semantic hits.
        merged: dict[str, RetrievedRecord] = {}
        for candidate in (*intent_candidates, *global_candidates):
            existing = merged.get(candidate.record_id)
            if existing is None or candidate.final_score > existing.final_score:
                merged[candidate.record_id] = candidate

        # Exact, high-confidence router matches (for example, "Tell me about
        # Aman") should still reach the explicitly requested public section if
        # the semantic score falls just below the global threshold. This is not
        # used for broad or low-confidence questions, which continue to return
        # no result when semantic retrieval finds no evidence.
        if not merged and self._can_use_intent_fallback(intent, relevant_intents):
            for record_id, semantic_score in zip(self._record_ids, semantic_scores, strict=True):
                record = self._knowledge_by_id[record_id]
                if record.category not in relevant_intents:
                    continue
                boost = self._intent_boost(record.category, intent)
                merged[record_id] = RetrievedRecord(
                    record_id=record.id,
                    title=record.title,
                    category=record.category,
                    source_section=record.source_section,
                    content=record.content,
                    semantic_score=round(float(semantic_score), 6),
                    applied_intent_boost=round(boost, 6),
                    final_score=round(float(semantic_score) + boost, 6),
                )
        return sorted(
            merged.values(),
            key=lambda candidate: (-candidate.final_score, -candidate.semantic_score, candidate.record_id),
        )[: self._config.max_results]

    def _can_use_intent_fallback(self, intent: IntentResult, relevant_intents: set[str]) -> bool:
        return (
            bool(relevant_intents)
            and intent.primary_intent != "general"
            and intent.confidence >= self._config.intent_fallback_confidence
            and bool(intent.matched_terms)
        )

    def _intent_boost(self, category: str, intent: IntentResult) -> float:
        if intent.primary_intent == "general":
            return 0.0
        if category == intent.primary_intent:
            return self._config.primary_intent_boost * intent.confidence
        if category in intent.related_intents:
            return self._config.related_intent_boost * intent.confidence
        return 0.0

    def _normalized_query_vector(self, question: str) -> np.ndarray:
        values = self._query_embedder(question) if self._query_embedder else self._embed_query(question)
        vector = np.asarray(list(values), dtype=np.float32)
        if vector.ndim != 1 or vector.size != self._dimension or not np.isfinite(vector).all():
            raise QueryEmbeddingError(
                f"Query embedding must contain {self._dimension} finite values to match the document index."
            )
        norm = float(np.linalg.norm(vector))
        if norm == 0:
            raise QueryEmbeddingError("Query embedding cannot be a zero vector.")
        return vector / norm

    def _embed_query(self, question: str) -> Iterable[float]:
        if not settings.gemini_api_key_configured:
            raise QueryEmbeddingError("GEMINI_API_KEY is missing; Ask Aman retrieval is unavailable.")
        if self._client is None:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        try:
            response = self._client.models.embed_content(
                model=self._model,
                contents=question,
                config=types.EmbedContentConfig(task_type=self._query_task_type),
            )
            embeddings = getattr(response, "embeddings", None)
            if not embeddings or not getattr(embeddings[0], "values", None):
                raise QueryEmbeddingError("Gemini returned a query embedding without vector values.")
            return embeddings[0].values
        except QueryEmbeddingError:
            raise
        except Exception as error:
            raise QueryEmbeddingError("Gemini could not generate a query embedding.") from error


def _load_default_retriever() -> HybridRetriever:
    try:
        knowledge_base = load_knowledge_base()
        index = _read_index(INDEX_PATH)
        return HybridRetriever(knowledge_base, index)
    except Exception as error:
        raise RetrievalInitializationError(f"Ask Aman retrieval initialization failed: {error}") from error


DEFAULT_RETRIEVER: HybridRetriever | None
DEFAULT_RETRIEVER_ERROR: RetrievalInitializationError | None
try:
    DEFAULT_RETRIEVER = _load_default_retriever()
    DEFAULT_RETRIEVER_ERROR = None
except RetrievalInitializationError as error:
    DEFAULT_RETRIEVER = None
    DEFAULT_RETRIEVER_ERROR = error


def get_default_retriever() -> HybridRetriever:
    """Return the single module-initialized retriever or a clear index readiness error."""

    if DEFAULT_RETRIEVER is None:
        raise DEFAULT_RETRIEVER_ERROR or RetrievalInitializationError(
            "Ask Aman retrieval initialization failed without a diagnostic."
        )
    return DEFAULT_RETRIEVER
