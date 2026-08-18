"""Regression tests for deterministic project-link answers."""

from __future__ import annotations

import unittest

from api.data_loader import load_knowledge_base
from api.intent_router import IntentRouter
from api.rag_service import RAGService


class StubRetriever:
    def __init__(self, records):
        self.knowledge_records = tuple(records)

    def retrieve(self, *_args, **_kwargs):
        return []


class NoGenerationService:
    def generate_answer(self, *_args, **_kwargs):
        raise AssertionError("Project-link answers must not use generation.")


class ProjectLinkRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        records = load_knowledge_base().records
        cls.service = RAGService(StubRetriever(records), IntentRouter(records), NoGenerationService())

    def test_project_link_requests_return_the_requested_verified_destination(self):
        cases = {
            "Share the Poetic Pebbles link.": "https://play.google.com/store/apps/details?id=com.tech.poeticpebbles",
            "Share the HireSense GitHub link.": "https://github.com/Amankaushik2810/HireSense-AI",
            "Share the Agri-Products GitHub link.": "https://github.com/Amankaushik2810/Agri-Products",
        }
        for question, expected_url in cases.items():
            with self.subTest(question=question):
                result = self.service.answer(question, [])
                self.assertEqual(result.intent, "projects")
                self.assertEqual(result.links[0].url, expected_url)


if __name__ == "__main__":
    unittest.main()
