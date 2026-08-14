"""Deterministic verified-link tests that never call Gemini."""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from api.data_loader import load_knowledge_base
from api.intent_router import IntentRouter
from api.models import KnowledgeRecord
from api.rag_service import RAGService
from api.retriever import RetrievedRecord
from scripts.validate_rag_data import validate_record


class NoGenerationService:
    def __init__(self) -> None:
        self.calls = 0

    def generate_answer(self, *_args, **_kwargs):
        self.calls += 1
        return "Generated project description."


class StubRetriever:
    def __init__(self, records, results=()):
        self.knowledge_records = tuple(records)
        self._results = list(results)
        self.retrieve_calls = 0

    def retrieve(self, _question, _intent):
        self.retrieve_calls += 1
        return self._results


class VerifiedProjectLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.knowledge_base = load_knowledge_base()
        cls.router = IntentRouter(cls.knowledge_base.records)
        cls.poetic_record = next(record for record in cls.knowledge_base.records if record.id == "project-poetic-pebbles-overview")

    def _service(self, results=()):
        generator = NoGenerationService()
        retriever = StubRetriever(self.knowledge_base.records, results)
        return RAGService(retriever, self.router, generator), retriever, generator

    def test_verified_poetic_pebbles_link_questions_bypass_gemini(self):
        questions = (
            "Can you share me the link of Poetic Pebbles?",
            "Give me the Poetic Pebbles Play Store link.",
            "Where can I download Poetic Pebbles?",
            "Is Poetic Pebbles available on Google Play?",
            "I want to install Poetic Pebbles.",
        )
        for question in questions:
            with self.subTest(question=question):
                service, retriever, generator = self._service()
                result = service.answer(question, [])
                self.assertEqual(result.answer, "You can download Poetic Pebbles directly from Google Play.")
                self.assertEqual(result.intent, "projects")
                self.assertEqual(generator.calls, 0)
                self.assertEqual(retriever.retrieve_calls, 0)
                self.assertEqual(
                    result.links[0].url,
                    "https://play.google.com/store/apps/details?id=com.tech.poeticpebbles",
                )
                self.assertEqual(result.links[0].label, "Download on Google Play")

    def test_unknown_project_link_is_not_invented_or_generated(self):
        service, retriever, generator = self._service()
        result = service.answer("Give me the link to an unknown project.", [])
        self.assertEqual(result.answer, "A verified public link for this project is not currently available in Aman's portfolio.")
        self.assertEqual(result.links, [])
        self.assertEqual(generator.calls, 0)
        self.assertEqual(retriever.retrieve_calls, 0)

    def test_normal_project_description_uses_rag_generation(self):
        retrieved = RetrievedRecord(
            record_id=self.poetic_record.id,
            title=self.poetic_record.title,
            category="projects",
            source_section="projects",
            content=self.poetic_record.content,
            semantic_score=0.9,
            applied_intent_boost=0.05,
            final_score=0.95,
        )
        service, retriever, generator = self._service([retrieved])
        result = service.answer("Tell me about Poetic Pebbles.", [])
        self.assertEqual(result.answer, "Generated project description.")
        self.assertEqual(result.links, [])
        self.assertEqual(generator.calls, 1)
        self.assertEqual(retriever.retrieve_calls, 1)

    def test_unsafe_link_values_are_rejected_by_schema_and_validator(self):
        unsafe_links = (
            "javascript:alert(1)",
            "data:text/html,unsafe",
            "http://play.google.com/store/apps/details?id=unsafe",
            "https://example.com/unsafe",
            "not a url",
        )
        for unsafe_url in unsafe_links:
            with self.subTest(unsafe_url=unsafe_url):
                unsafe_link = {
                    "id": "unsafe-link",
                    "label": "Unsafe",
                    "url": unsafe_url,
                    "type": "play_store",
                }
                with self.assertRaises(ValidationError):
                    KnowledgeRecord.model_validate({
                        "id": "project-test",
                        "category": "projects",
                        "title": "Test project",
                        "content": "Test content",
                        "keywords": ["test"],
                        "source_section": "projects",
                        "links": [unsafe_link],
                    })
        unsafe_link = {"id": "unsafe-link", "label": "Unsafe", "url": "javascript:alert(1)", "type": "play_store"}
        errors = validate_record(
            {
                "id": "project-test",
                "category": "projects",
                "title": "Test project",
                "content": "Test content",
                "keywords": ["test"],
                "source_section": "projects",
                "links": [unsafe_link],
            },
            "projects.json",
            0,
            set(),
            set(),
        )
        self.assertTrue(any("valid HTTPS URL" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
