"""Regression checks for Vercel FastAPI function discovery."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from fastapi import FastAPI

from api.data_loader import load_knowledge_base
from api.index import app
from scripts.build_index import INDEX_PATH, _read_index, validate_index


PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent


class VercelDeploymentTests(unittest.TestCase):
    def test_required_deployment_files_are_at_the_application_root(self):
        for relative_path in (
            "api/index.py",
            "requirements.txt",
            "vercel.json",
            "package.json",
            "rag_data/vectors.json",
        ):
            with self.subTest(relative_path=relative_path):
                self.assertTrue((PROJECT_DIRECTORY / relative_path).is_file())

    def test_fastapi_app_and_health_route_are_discoverable(self):
        self.assertIsInstance(app, FastAPI)
        route_paths = [route.path for route in app.routes]
        self.assertEqual(route_paths.count("/api/health"), 1)
        self.assertEqual(route_paths.count("/api/ask"), 1)

    def test_vercel_config_rewrites_only_api_requests_to_fastapi(self):
        config = json.loads((PROJECT_DIRECTORY / "vercel.json").read_text(encoding="utf-8"))
        self.assertEqual(config["framework"], "vite")
        self.assertEqual(config["buildCommand"], "npm run build")
        self.assertEqual(config["outputDirectory"], "dist")
        self.assertIn("api/index.py", config["functions"])
        self.assertEqual(config["functions"]["api/index.py"]["includeFiles"], "rag_data/**")
        self.assertNotIn("builds", config)
        self.assertNotIn("routes", config)
        self.assertEqual(
            config["rewrites"],
            [{"source": "/api/(.*)", "destination": "/api/index.py"}],
        )

    def test_bundled_vector_index_is_available_and_complete(self):
        knowledge_base = load_knowledge_base()
        index = _read_index(INDEX_PATH)
        self.assertEqual(len(knowledge_base.records), 66)
        self.assertEqual(validate_index(index, knowledge_base), 3072)


if __name__ == "__main__":
    unittest.main()
