import unittest

from fastapi.testclient import TestClient

from api import index as api_index
from api.gemini_service import GeminiQuotaError, GeminiTemporaryError, GeminiTimeoutError
from api.models import AskAmanResponse, SourceReference
from api.rag_service import InformationUnavailableError, RetrievalUnavailableError
from api.retriever import RetrievalInitializationError


class FakeRagService:
    def __init__(self):
        self.history_lengths = []

    def answer(self, _question, history):
        self.history_lengths.append(len(history))
        return AskAmanResponse(
            answer="Aman has practical experience with RAG and LLM workflows.",
            sources=[SourceReference(title="Applied AI skills", section="skills")],
            suggestions=["What AI skills does Aman use?"],
            intent="skills",
        )


class AskAmanEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(api_index.app)
        self.original_get_service = api_index.get_rag_service
        api_index.rate_limiter.clear()

    def tearDown(self):
        api_index.get_rag_service = self.original_get_service
        api_index.rate_limiter.clear()

    def _raise(self, error):
        def callback():
            raise error

        return callback

    def test_grounded_response_is_structured_and_not_cached(self):
        fake_service = FakeRagService()
        api_index.get_rag_service = lambda: fake_service
        response = self.client.post(
            "/api/ask",
            json={
                "question": "What is Aman's experience with RAG?",
                "history": [{"question": "What does Aman do?", "answer": "He is an AI/ML engineer."}],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.json()["intent"], "skills")
        self.assertEqual(response.json()["sources"][0], {"title": "Applied AI skills", "section": "skills"})
        self.assertEqual(fake_service.history_lengths, [1])

    def test_invalid_question_has_friendly_error(self):
        response = self.client.post("/api/ask", json={"question": "x" * 301, "history": []})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.json()["error"]["code"], "invalid_question")

    def test_missing_index_has_friendly_error(self):
        api_index.get_rag_service = self._raise(RetrievalInitializationError("vectors.json missing"))
        response = self.client.post("/api/ask", json={"question": "Tell me about Aman.", "history": []})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "index_unavailable")

    def test_provider_and_information_errors_are_mapped(self):
        cases = [
            (GeminiQuotaError("quota"), 429, "gemini_quota_exhausted"),
            (GeminiTimeoutError("timeout"), 504, "gemini_timeout"),
            (GeminiTemporaryError("temporary"), 503, "gemini_temporarily_unavailable"),
            (RetrievalUnavailableError("retrieval unavailable"), 503, "retrieval_unavailable"),
            (InformationUnavailableError("not available"), 404, "information_unavailable"),
        ]
        for error, status_code, code in cases:
            with self.subTest(code=code):
                api_index.rate_limiter.clear()
                api_index.get_rag_service = self._raise(error)
                response = self.client.post("/api/ask", json={"question": "Question?", "history": []})
                self.assertEqual(response.status_code, status_code)
                self.assertEqual(response.json()["error"]["code"], code)

    def test_rate_limit_is_short_window_and_health_never_uses_rag(self):
        fake_service = FakeRagService()
        api_index.get_rag_service = lambda: fake_service
        for _ in range(8):
            self.assertEqual(self.client.post("/api/ask", json={"question": "Question?", "history": []}).status_code, 200)
        limited = self.client.post("/api/ask", json={"question": "Question?", "history": []})
        self.assertEqual(limited.status_code, 429)
        self.assertEqual(limited.json()["error"]["code"], "rate_limited")

        api_index.get_rag_service = lambda: (_ for _ in ()).throw(AssertionError("Health must not access RAG"))
        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)


if __name__ == "__main__":
    unittest.main()
