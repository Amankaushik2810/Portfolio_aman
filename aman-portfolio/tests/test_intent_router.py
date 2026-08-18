import unittest

from api.data_loader import load_knowledge_base
from api.intent_router import IntentRouter, IntentSignals


class IntentRouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = IntentRouter(load_knowledge_base().records)

    def test_requested_single_intent_questions(self):
        cases = {
            "Tell me about Aman.": "about",
            "Where did Aman complete B.Tech?": "education",
            "What are his AI and machine-learning skills?": "skills",
            "Tell me about Poetic Pebbles.": "projects",
            "Where does Aman work?": "experience",
            "How can I contact Aman?": "contact",
            "What can I ask you?": "faq",
        }
        for question, expected_intent in cases.items():
            with self.subTest(question=question):
                result = self.router.route(question)
                self.assertEqual(result.primary_intent, expected_intent)
                self.assertGreater(result.confidence, 0.0)
                self.assertTrue(result.matched_terms)

    def test_project_and_skills_question_has_multiple_intents(self):
        result = self.router.route("Which skills did Aman use in Poetic Pebbles?")
        self.assertEqual(result.primary_intent, "projects")
        self.assertIn("skills", result.related_intents)
        self.assertIn("poetic pebbles", result.matched_terms)

    def test_experience_and_skills_question_has_multiple_intents(self):
        result = self.router.route("What AI skills does Aman use at GlobalLogic?")
        self.assertEqual(result.primary_intent, "skills")
        self.assertIn("experience", result.related_intents)
        self.assertIn("globallogic", result.matched_terms)

    def test_broad_question_uses_general_fallback(self):
        result = self.router.route("Tell me everything about Aman.")
        self.assertEqual(result.primary_intent, "general")
        self.assertIn("projects", result.related_intents)
        self.assertEqual(result.confidence, 0.2)

    def test_greeting_and_low_confidence_questions_use_general(self):
        greeting = self.router.route("Hello!")
        unknown = self.router.route("What is the weather tomorrow?")
        self.assertEqual(greeting.primary_intent, "general")
        self.assertEqual(unknown.primary_intent, "general")
        self.assertGreater(greeting.confidence, unknown.confidence)

    def test_name_alone_is_not_hard_routed_to_about(self):
        result = self.router.route("Aman")
        self.assertEqual(result.primary_intent, "general")

    def test_keyword_configuration_can_be_extended(self):
        router = IntentRouter(
            signal_overrides={
                "about": IntentSignals(keywords=("biography",), phrases=(), entities=())
            }
        )
        self.assertEqual(router.route("Share a biography.").primary_intent, "about")

    def test_project_link_requests_have_external_link_action(self):
        cases = {
            "Can you share me the link of Poetic Pebbles?": "poetic pebbles",
            "Share the Poetic Pebbles link.": "poetic pebbles",
            "Share the HireSense GitHub link.": "hiresense",
            "Share the Agri-Products GitHub link.": "agri products",
        }
        for question, expected_term in cases.items():
            with self.subTest(question=question):
                result = self.router.route(question)
                self.assertEqual(result.primary_intent, "projects")
                self.assertIn("external_link", result.actions)
                self.assertIn(expected_term, result.matched_terms)


if __name__ == "__main__":
    unittest.main()
