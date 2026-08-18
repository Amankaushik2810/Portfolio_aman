"""Vercel-compatible FastAPI entry point for Ask Aman."""

from __future__ import annotations

import hashlib
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import settings
from api.data_loader import KnowledgeBase, load_knowledge_base
from api.errors import KnowledgeLoadError
from api.gemini_service import GeminiQuotaError, GeminiServiceError, GeminiTemporaryError, GeminiTimeoutError
from api.models import (
    AskAmanRequest,
    AskAmanResponse,
    ConfigurationHealth,
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    IndexHealth,
    KnowledgeHealth,
)
from api.rag_service import InformationUnavailableError, RetrievalUnavailableError, get_rag_service
from api.retriever import DEFAULT_RETRIEVER, RetrievalInitializationError


app = FastAPI(title="Ask Aman API", version="0.1.0", docs_url=None, redoc_url=None, openapi_url=None)

if not settings.is_production:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["POST", "GET"],
        allow_headers=["Content-Type"],
    )


class PublicApiError(RuntimeError):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class ShortWindowRateLimiter:
    """Best-effort in-memory protection; only short-lived hashed client identifiers are kept."""

    def __init__(self, limit: int = 8, window_seconds: int = 60) -> None:
        self._limit = limit
        self._window_seconds = window_seconds
        self._entries: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, client_host: str) -> bool:
        client_key = hashlib.sha256(client_host.encode("utf-8")).hexdigest()[:16]
        now = time.monotonic()
        with self._lock:
            entries = self._entries[client_key]
            while entries and now - entries[0] >= self._window_seconds:
                entries.popleft()
            if len(entries) >= self._limit:
                return False
            entries.append(now)
            return True

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()


rate_limiter = ShortWindowRateLimiter(settings.rate_limit, settings.rate_window_seconds)


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(error=ErrorDetail(code=code, message=message)).model_dump(),
        headers={"Cache-Control": "no-store"},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, _error: RequestValidationError) -> JSONResponse:
    return _error_response(422, "invalid_question", "Provide a question of up to 300 characters and at most two recent exchanges.")


@app.exception_handler(PublicApiError)
async def public_api_error_handler(_request: Request, error: PublicApiError) -> JSONResponse:
    return _error_response(error.status_code, error.code, error.message)


@app.exception_handler(Exception)
async def unexpected_error_handler(_request: Request, _error: Exception) -> JSONResponse:
    return _error_response(500, "internal_error", "Ask Aman could not complete that request right now.")


@app.middleware("http")
async def limit_ask_aman_request_body(request: Request, call_next):
    """Reject oversized Ask Aman bodies before JSON validation or provider access."""

    if request.method == "POST" and request.url.path == "/api/ask":
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > settings.max_request_body_bytes:
            return _error_response(413, "request_too_large", "Ask Aman requests are limited to a safe size.")
        body = await request.body()
        if len(body) > settings.max_request_body_bytes:
            return _error_response(413, "request_too_large", "Ask Aman requests are limited to a safe size.")
    return await call_next(request)

knowledge_base: KnowledgeBase | None
try:
    knowledge_base = load_knowledge_base()
except KnowledgeLoadError:
    # Keep the function importable so /api/health can report degraded readiness.
    knowledge_base = None


@app.get("/api/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Report local readiness without calling Gemini or exposing configuration values."""

    loaded = knowledge_base is not None
    index_loaded = DEFAULT_RETRIEVER is not None
    return HealthResponse(
        status="ok" if loaded and index_loaded else "degraded",
        knowledge=KnowledgeHealth(
            loaded=loaded,
            record_count=len(knowledge_base.records) if knowledge_base else 0,
            categories=knowledge_base.category_counts if knowledge_base else {},
        ),
        index=IndexHealth(
            loaded=index_loaded,
            record_count=DEFAULT_RETRIEVER.indexed_record_count if DEFAULT_RETRIEVER else 0,
            embedding_dimension=DEFAULT_RETRIEVER.embedding_dimension if DEFAULT_RETRIEVER else None,
        ),
        configuration=ConfigurationHealth(
            gemini_api_key_configured=settings.gemini_api_key_configured,
            generation_model_configured=settings.generation_model_configured,
            embedding_model_configured=settings.embedding_model_configured,
        ),
    )


@app.post(
    "/api/ask",
    response_model=AskAmanResponse,
    responses={
        404: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
)
def ask_aman(payload: AskAmanRequest, request: Request, response: Response) -> AskAmanResponse:
    """Return a transient grounded answer; no visitor message is logged or stored."""

    client_host = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(client_host):
        raise PublicApiError(429, "rate_limited", "Please wait a moment before asking another question.")

    try:
        answer = get_rag_service().answer(payload.question, payload.history[-2:])
    except RetrievalInitializationError as error:
        raise PublicApiError(503, "index_unavailable", "Ask Aman is still being prepared. Please try again later.") from error
    except RetrievalUnavailableError as error:
        raise PublicApiError(503, "retrieval_unavailable", str(error)) from error
    except InformationUnavailableError as error:
        raise PublicApiError(404, "information_unavailable", str(error)) from error
    except GeminiQuotaError as error:
        raise PublicApiError(429, "gemini_quota_exhausted", str(error)) from error
    except GeminiTimeoutError as error:
        raise PublicApiError(504, "gemini_timeout", str(error)) from error
    except GeminiTemporaryError as error:
        raise PublicApiError(503, "gemini_temporarily_unavailable", str(error)) from error
    except GeminiServiceError as error:
        raise PublicApiError(503, "gemini_unavailable", str(error)) from error
    except Exception as error:
        raise PublicApiError(500, "internal_error", "Ask Aman could not complete that request right now.") from error

    response.headers["Cache-Control"] = "no-store"
    return answer
