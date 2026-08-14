import unittest

from api.data_loader import load_knowledge_base
from api.intent_router import IntentResult, IntentRouter
from api.retriever import HybridRetriever, RetrievalInitializationError
from scripts.build_index import (
    DOCUMENT_TASK_TYPE,
    INDEX_VERSION,
    QUERY_TASK_TYPE,
    content_fingerprint,
)


class HybridRetrieverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.knowledge_base = load_knowledge_base()
        cls.router = IntentRouter(cls.knowledge_base.records)
        cls.index = cls._build_test_index()

    @classmethod
    def _build_test_index(cls):
        vectors = []
        special_vectors = {
            "about-profile": [0.8, 0.6, 0.0, 0.0, 0.0],
            "project-poetic-pebbles-overview": [0.0, 1.0, 0.0, 0.0, 0.0],
            "project-poetic-pebbles-features": [0.0, 0.7, 0.7, 0.0, 0.0],
            "skills-applied-ai": [0.0, 0.0, 1.0, 0.0, 0.0],
            "experience-globallogic-role": [0.0, 0.0, 0.7, 0.7, 0.0],
        }
        for record in cls.knowledge_base.records:
            vectors.append(
                {
                    "record_id": record.id,
                    "category": record.category,
                    "title": record.title,
                    "source_section": record.source_section,
                    "embedding": special_vectors.get(record.id, [-1.0, 0.0, 0.0, 0.0, 0.0]),
                    "content_fingerprint": content_fingerprint(record),
                    "embedding_model": "test-embedding-model",
                    "index_version": INDEX_VERSION,
                }
            )
        return {
            "index_version": INDEX_VERSION,
            "embedding_model": "test-embedding-model",
            "embedding_dimension": 5,
            "record_count": len(vectors),
            "document_task_type": DOCUMENT_TASK_TYPE,
            "query_task_type": QUERY_TASK_TYPE,
            "vectors": vectors,
        }

    def _retriever(self, query_vector):
        return HybridRetriever(self.knowledge_base, self.index, query_embedder=lambda _question: query_vector)

    def test_high_confidence_named_project_ranking_and_public_fields(self):
        results = self._retriever([0.0, 1.0, 0.0, 0.0, 0.0]).retrieve(
            "Tell me about Poetic Pebbles.", self.router.route("Tell me about Poetic Pebbles.")
        )
        self.assertEqual(results[0].record_id, "project-poetic-pebbles-overview")
        self.assertGreater(results[0].applied_intent_boost, 0.0)
        self.assertEqual(results[0].category, "projects")
        self.assertTrue(results[0].content)
        self.assertFalse(hasattr(results[0], "embedding"))

    def test_primary_category_boost_can_prioritize_close_semantic_results(self):
        intent = IntentResult("projects", (), 0.8, ("poetic pebbles",))
        results = self._retriever([0.0, 0.69, 0.72, 0.0, 0.0]).retrieve("Poetic Pebbles", intent)
        self.assertEqual(results[0].category, "projects")
        self.assertGreater(results[0].final_score, results[0].semantic_score)

    def test_multiple_intents_keep_experience_and_skills(self):
        results = self._retriever([0.0, 0.0, 1.0, 1.0, 0.0]).retrieve(
            "What AI skills does Aman use at GlobalLogic?",
            self.router.route("What AI skills does Aman use at GlobalLogic?"),
        )
        categories = {result.category for result in results}
        self.assertIn("skills", categories)
        self.assertIn("experience", categories)

    def test_low_confidence_general_search_uses_global_semantic_results(self):
        general = IntentResult("general", (), 0.2, ())
        results = self._retriever([0.0, 0.0, 1.0, 0.0, 0.0]).retrieve("A broad question", general)
        self.assertEqual(results[0].record_id, "skills-applied-ai")
        self.assertEqual(results[0].applied_intent_boost, 0.0)

    def test_global_fallback_keeps_relevant_project_when_router_selects_about(self):
        about = IntentResult("about", (), 0.9, ("about aman",))
        results = self._retriever([0.0, 1.0, 0.0, 0.0, 0.0]).retrieve("Aman", about)
        self.assertEqual(results[0].category, "projects")

    def test_merge_deduplicates_overlapping_global_and_intent_candidates(self):
        results = self._retriever([0.0, 1.0, 0.0, 0.0, 0.0]).retrieve(
            "Tell me about Poetic Pebbles.", self.router.route("Tell me about Poetic Pebbles.")
        )
        self.assertEqual(len(results), len({result.record_id for result in results}))
        self.assertLessEqual(len(results), 3)

    def test_missing_information_returns_no_results(self):
        results = self._retriever([0.0, 0.0, 0.0, 0.0, 1.0]).retrieve(
            "What is Aman's favourite food?", IntentResult("general", (), 0.2, ())
        )
        self.assertEqual(results, [])

    def test_high_confidence_explicit_about_request_has_intent_fallback(self):
        # Simulate an embedding below the semantic threshold. The exact
        # high-confidence router phrase must still retrieve About records.
        results = self._retriever([0.0, 0.0, 0.0, 0.0, 1.0]).retrieve(
            "Tell me about Aman.", self.router.route("Tell me about Aman.")
        )
        self.assertTrue(results)
        self.assertLessEqual(len(results), 3)
        self.assertTrue(all(result.category == "about" for result in results))
        self.assertGreater(results[0].applied_intent_boost, 0.0)

    def test_stale_index_fails_clearly(self):
        stale_index = dict(self.index)
        stale_index["vectors"] = stale_index["vectors"][:-1]
        stale_index["record_count"] -= 1
        with self.assertRaises(RetrievalInitializationError):
            HybridRetriever(self.knowledge_base, stale_index, query_embedder=lambda _question: [1, 0, 0, 0, 0])


if __name__ == "__main__":
    unittest.main()
