"""Offline Kaushik's Footprints knowledge and verified-link checks."""

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
        raise AssertionError("Verified GitHub links must not use generation.")


class KaushikFootprintsKnowledgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_knowledge_base().records
        cls.by_id = {record.id: record for record in cls.records}

    def test_focused_records_cover_verified_scope_and_limits(self):
        expected = {
            "project-kaushik-footprints-overview": ("fashion and lifestyle", "does not claim completed live payments"),
            "project-kaushik-footprints-features": ("JWT-based", "persisted in MongoDB", "live payments are not presented as implemented"),
            "project-kaushik-footprints-technologies": ("Node.js and Express", "Multer"),
            "project-kaushik-footprints-challenges": ("CORS", "next-stage engineering"),
            "project-kaushik-footprints-lessons": ("full-stack features", "modular"),
        }
        for record_id, phrases in expected.items():
            with self.subTest(record_id=record_id):
                for phrase in phrases:
                    self.assertIn(phrase, self.by_id[record_id].content)

    def test_verified_github_link_is_returned_without_generation(self):
        service = RAGService(StubRetriever(self.records), IntentRouter(self.records), NoGenerationService())
        result = service.answer("Can you share the Kaushik Footprints GitHub link?", [])
        self.assertEqual(result.links[0].url, "https://github.com/Amankaushik2810/Kaushik-s-Footprints")
        self.assertEqual(result.links[0].type, "github")


if __name__ == "__main__":
    unittest.main()
