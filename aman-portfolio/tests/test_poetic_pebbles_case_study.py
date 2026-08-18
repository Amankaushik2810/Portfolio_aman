"""Regression checks for the public Poetic Pebbles case study and RAG facts."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


PROJECT_DIRECTORY = Path(__file__).resolve().parents[1]
PROJECTS_JSON = PROJECT_DIRECTORY / "rag_data" / "projects.json"
PROJECTS_COMPONENT = PROJECT_DIRECTORY / "src" / "data" / "projects.js"
CASE_STUDY_COMPONENT = PROJECT_DIRECTORY / "src" / "components" / "sections" / "PoeticPebblesCaseStudy.jsx"
ARCHITECTURE_COMPONENT = PROJECT_DIRECTORY / "src" / "components" / "sections" / "ProjectArchitecture.jsx"


class PoeticPebblesCaseStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads(PROJECTS_JSON.read_text(encoding="utf-8"))
        cls.by_id = {record["id"]: record for record in cls.records}

    def test_focused_knowledge_records_cover_the_visible_case_study(self):
        expected_ids = {
            "project-poetic-pebbles-overview",
            "project-poetic-pebbles-ownership-timeline",
            "project-poetic-pebbles-architecture",
            "project-poetic-pebbles-publishing-workflow",
            "project-poetic-pebbles-administrative-application",
            "project-poetic-pebbles-firebase-services",
            "project-poetic-pebbles-challenges",
            "project-poetic-pebbles-lessons-learned",
            "project-poetic-pebbles-community-impact",
            "project-poetic-pebbles-instagram-community",
            "project-poetic-pebbles-ai-roadmap",
        }
        self.assertTrue(expected_ids.issubset(self.by_id))
        self.assertIn("not currently live", self.by_id["project-poetic-pebbles-ai-roadmap"]["content"])

    def test_verified_play_store_link_is_preserved_in_structured_metadata(self):
        links = self.by_id["project-poetic-pebbles-overview"]["links"]
        self.assertEqual(links, [{
            "id": "poetic-pebbles-play-store",
            "label": "Download on Google Play",
            "url": "https://play.google.com/store/apps/details?id=com.tech.poeticpebbles",
            "type": "play_store",
        }])

    def test_case_study_is_rendered_from_structured_content_with_safe_store_action(self):
        source = PROJECTS_COMPONENT.read_text(encoding="utf-8")
        component = CASE_STUDY_COMPONENT.read_text(encoding="utf-8")
        architecture = ARCHITECTURE_COMPONENT.read_text(encoding="utf-8")
        self.assertIn("Poetic Pebbles AI — In development", source)
        self.assertIn("https://play.google.com/store/apps/details?id=com.tech.poeticpebbles", source)
        self.assertIn("Architecture / workflow", component)
        self.assertIn("In development", architecture)
        self.assertIn("ProjectLinks", component)


if __name__ == "__main__":
    unittest.main()
