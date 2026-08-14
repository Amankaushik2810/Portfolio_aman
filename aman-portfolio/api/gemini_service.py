"""Small, timeout-bounded Gemini generation wrapper for grounded answers."""

from __future__ import annotations

from collections.abc import Sequence

from google import genai
from google.genai import types

from api.config import settings
from api.models import ConversationExchange


# A normal grounded response can approach 12 seconds on a cold provider path.
# Keep a finite limit while leaving enough headroom for the local Vite proxy and
# Vercel function overhead.
GENERATION_TIMEOUT_MS = 20_000
MAX_OUTPUT_TOKENS = 250


class GeminiServiceError(RuntimeError):
    """Base error for safe provider-facing failures."""


class GeminiQuotaError(GeminiServiceError):
    """The provider rejected the request because of quota or rate limits."""


class GeminiTimeoutError(GeminiServiceError):
    """The provider did not respond before the configured timeout."""


class GeminiTemporaryError(GeminiServiceError):
    """The provider is temporarily unavailable."""


def _status_code(error: Exception) -> int | None:
    for attribute in ("status_code", "code"):
        value = getattr(error, attribute, None)
        if isinstance(value, int):
            return value
    return None


def _history_text(history: Sequence[ConversationExchange]) -> str:
    if not history:
        return ""
    exchanges = []
    for exchange in history[-2:]:
        exchanges.append(
            f"Previous visitor question: {exchange.question}\nPrevious assistant answer: {exchange.answer}"
        )
    return "\n\n".join(exchanges)


class GeminiService:
    """Creates one lazy Gemini client and does not retain visitor messages."""

    def __init__(self) -> None:
        self._client: genai.Client | None = None

    def generate_answer(
        self,
        system_prompt: str,
        question: str,
        history: Sequence[ConversationExchange],
    ) -> str:
        if not settings.gemini_api_key_configured:
            raise GeminiServiceError("Gemini is not configured for this deployment.")
        if self._client is None:
            self._client = genai.Client(
                api_key=settings.gemini_api_key,
                http_options=types.HttpOptions(timeout=GENERATION_TIMEOUT_MS),
            )

        history_text = _history_text(history)
        contents = "\n\n".join(part for part in (history_text, f"Current visitor question: {question}") if part)
        try:
            response = self._client.models.generate_content(
                model=settings.gemini_generation_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    candidate_count=1,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                ),
            )
        except Exception as error:  # Provider exception classes vary between SDK releases.
            status = _status_code(error)
            message = str(error).lower()
            if status == 429 or "quota" in message or "resource exhausted" in message:
                raise GeminiQuotaError("Gemini is temporarily at its request limit. Please try again shortly.") from error
            if status in {408, 504} or "timeout" in message or "timed out" in message:
                raise GeminiTimeoutError("Gemini took too long to respond. Please try again.") from error
            if status in {500, 502, 503} or "unavailable" in message or "temporarily" in message:
                raise GeminiTemporaryError("Gemini is temporarily unavailable. Please try again shortly.") from error
            raise GeminiServiceError("Ask Aman could not generate an answer right now.") from error

        answer = (getattr(response, "text", None) or "").strip()
        if not answer:
            raise GeminiTemporaryError("Gemini returned an empty answer. Please try again.")
        return answer
