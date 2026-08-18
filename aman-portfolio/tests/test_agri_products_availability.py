"""Offline checks for Agri-Products availability messaging and public links."""

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
        raise AssertionError("Availability answers must not use generation.")


class AgriProductsAvailabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_knowledge_base().records
        cls.service = RAGService(StubRetriever(cls.records), IntentRouter(cls.records), NoGenerationService())

    def test_live_demo_answer_reports_the_outage_and_returns_github(self):
        result = self.service.answer("Can you share the Agri-Products live demo?", [])
        self.assertIn("temporarily unavailable", result.answer)
        self.assertIn("backend service is currently offline", result.answer)
        self.assertEqual(result.links[0].url, "https://github.com/Amankaushik2810/Agri-Products")
        self.assertEqual(result.links[0].type, "github")


if __name__ == "__main__":
    unittest.main()
