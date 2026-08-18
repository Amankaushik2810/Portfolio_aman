"""Offline HireSense AI knowledge and deterministic-link checks."""

from __future__ import annotations

import unittest

from api.data_loader import load_knowledge_base
from api.intent_router import IntentRouter
from api.rag_service import RAGService


class NoGenerationService:
    def generate_answer(self, *_args, **_kwargs):
        raise AssertionError("Verified GitHub links must not use generation.")


class StubRetriever:
    def __init__(self, records):
        self.knowledge_records = tuple(records)

    def retrieve(self, *_args, **_kwargs):
        return []


class HireSenseCaseStudyKnowledgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = load_knowledge_base().records
        cls.by_id = {record.id: record for record in cls.records}

    def test_focused_records_answer_the_documented_questions(self):
        expected_records = {
            "project-hiresense-ai-overview": ("Aman Kaushik", "advisory"),
            "project-hiresense-ai-timeline-status": ("April 2026", "deployment is being prepared"),
            "project-hiresense-ai-input-modes": ("CSV", "text-based PDF", "manually entered"),
            "project-hiresense-ai-preprocessing": ("normalizes", "extracts candidate name"),
            "project-hiresense-ai-classification": ("96.88% accuracy", "100.00% precision", "93.75% recall", "96.77% F1", "99.68%"),
            "project-hiresense-ai-match-score-status": ("still includes shortlist status", "not fixed"),
            "project-hiresense-ai-rag-retrieval": ("five most relevant", "cosine similarity"),
            "project-hiresense-ai-local-llm": ("Llama 3.2", "Ollama"),
            "project-hiresense-ai-interview-threshold": ("above 75%",),
            "project-hiresense-ai-responsible-ai": ("not an autonomous hiring system", "does not represent production hiring accuracy"),
            "project-hiresense-ai-improvement-roadmap": ("timeout and retry handling", "In progress"),
        }
        for record_id, phrases in expected_records.items():
            with self.subTest(record_id=record_id):
                content = self.by_id[record_id].content
                for phrase in phrases:
                    self.assertIn(phrase, content)

    def test_verified_github_question_returns_clickable_structured_link(self):
        service = RAGService(StubRetriever(self.records), IntentRouter(self.records), NoGenerationService())
        result = service.answer("Can you share the HireSense AI GitHub link?", [])
        self.assertEqual(result.intent, "projects")
        self.assertEqual(result.links[0].id, "hiresense-ai-github")
        self.assertEqual(result.links[0].url, "https://github.com/Amankaushik2810/HireSense-AI")
        self.assertEqual(result.links[0].type, "github")


if __name__ == "__main__":
    unittest.main()
