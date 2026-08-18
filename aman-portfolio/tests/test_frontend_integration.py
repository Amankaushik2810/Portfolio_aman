"""Regression checks for the same-origin React-to-FastAPI development contract."""

from __future__ import annotations

import unittest
import json
from pathlib import Path


PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent


class FrontendIntegrationTests(unittest.TestCase):
    def test_react_uses_only_same_origin_api_ask_path(self):
        api_client = (PROJECT_DIRECTORY / "src" / "components" / "AskAman" / "askAmanApi.js").read_text(encoding="utf-8")
        self.assertIn("const API_PATH = '/api/ask'", api_client)
        self.assertNotIn("GEMINI_API_KEY", api_client)
        self.assertNotIn("localhost:8000", api_client)

    def test_vite_proxy_preserves_complete_api_path(self):
        vite_config = (PROJECT_DIRECTORY / "vite.config.js").read_text(encoding="utf-8")
        self.assertIn("'/api'", vite_config)
        self.assertIn("http://127.0.0.1:8000", vite_config)
        self.assertNotIn("rewrite:", vite_config)

    def test_vercel_config_keeps_fastapi_separate_from_static_output(self):
        config = json.loads((PROJECT_DIRECTORY / "vercel.json").read_text(encoding="utf-8"))
        self.assertEqual(config["framework"], "vite")
        self.assertEqual(config["buildCommand"], "npm run build")
        self.assertEqual(config["outputDirectory"], "dist")
        function = config["functions"]["api/index.py"]
        self.assertEqual(function["maxDuration"], 30)
        self.assertEqual(function["includeFiles"], "rag_data/**")
        self.assertNotIn("builds", config)
        self.assertNotIn("routes", config)
        self.assertEqual(
            config["rewrites"],
            [{"source": "/api/(.*)", "destination": "/api/index.py"}],
        )

    def test_chat_renders_backend_answer_and_source_badges_as_text(self):
        chat_message = (PROJECT_DIRECTORY / "src" / "components" / "AskAman" / "ChatMessage.jsx").read_text(encoding="utf-8")
        self.assertIn("{message.content}", chat_message)
        self.assertIn("ask-aman-source", chat_message)
        self.assertNotIn("dangerouslySetInnerHTML", chat_message)

    def test_chat_renders_verified_links_with_safe_new_tab_attributes(self):
        chat_message = (PROJECT_DIRECTORY / "src" / "components" / "AskAman" / "ChatMessage.jsx").read_text(encoding="utf-8")
        api_client = (PROJECT_DIRECTORY / "src" / "components" / "AskAman" / "askAmanApi.js").read_text(encoding="utf-8")
        self.assertIn('target="_blank"', chat_message)
        self.assertIn('rel="noopener noreferrer"', chat_message)
        self.assertIn("Download on Google Play", (PROJECT_DIRECTORY / "rag_data" / "projects.json").read_text(encoding="utf-8"))
        self.assertIn("APPROVED_LINK_HOSTS", api_client)
        self.assertIn("new URL(link.url)", api_client)


if __name__ == "__main__":
    unittest.main()
