"""Build or validate the compact Gemini embedding index for Ask Aman."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np
from google import genai
from google.genai import types

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
if str(PROJECT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIRECTORY))

from api.config import settings
from api.data_loader import KnowledgeBase, load_knowledge_base
from api.models import KnowledgeRecord


INDEX_VERSION = "1"
INDEX_PATH = PROJECT_DIRECTORY / "rag_data" / "vectors.json"
MAX_INDEX_BYTES = 3 * 1024 * 1024
MAX_RETRIES = 4
RETRY_DELAYS_SECONDS = (1, 2, 4)
DOCUMENT_TASK_TYPE = "RETRIEVAL_DOCUMENT"
QUERY_TASK_TYPE = "RETRIEVAL_QUERY"


class IndexBuildError(RuntimeError):
    """Raised for safe, user-facing index build failures."""


class IndexValidationError(RuntimeError):
    """Raised when a saved vector index is malformed or stale."""


def build_embedding_text(record: KnowledgeRecord) -> str:
    """Create stable, retrieval-focused text from public record fields."""

    return "\n".join(
        (
            f"Title: {record.title}",
            f"Category: {record.category}",
            f"Source section: {record.source_section}",
            f"Keywords: {', '.join(record.keywords)}",
            f"Content: {record.content}",
        )
    )


def content_fingerprint(record: KnowledgeRecord) -> str:
    """Fingerprint every field that affects a document embedding."""

    payload = {
        "title": record.title,
        "category": record.category,
        "source_section": record.source_section,
        "keywords": record.keywords,
        "content": record.content,
        "links": [link.model_dump() for link in record.links],
    }
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _response_vector(response: Any) -> list[float]:
    embeddings = getattr(response, "embeddings", None)
    if not embeddings or not getattr(embeddings[0], "values", None):
        raise IndexBuildError("Gemini returned an embedding response without vector values.")
    return [round(float(value), 8) for value in embeddings[0].values]


def _status_code(error: Exception) -> int | None:
    for attribute in ("status_code", "code"):
        value = getattr(error, attribute, None)
        if isinstance(value, int):
            return value
    return None


def _is_temporary_error(error: Exception) -> bool:
    status = _status_code(error)
    if status in {408, 429, 500, 502, 503, 504}:
        return True
    message = str(error).lower()
    return any(fragment in message for fragment in ("timeout", "temporarily", "unavailable", "rate limit", "resource exhausted"))


def _credential_error(error: Exception) -> bool:
    status = _status_code(error)
    if status in {401, 403}:
        return True
    message = str(error).lower()
    return "api key" in message and any(fragment in message for fragment in ("invalid", "missing", "not valid", "not found"))


def embed_document(client: genai.Client, record: KnowledgeRecord, model: str) -> list[float]:
    """Embed one document with bounded retry handling and no secret logging."""

    config = types.EmbedContentConfig(
        task_type=DOCUMENT_TASK_TYPE,
        title=record.title,
    )
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.embed_content(
                model=model,
                contents=build_embedding_text(record),
                config=config,
            )
            return _response_vector(response)
        except Exception as error:  # SDK error classes vary by transport and release.
            if _credential_error(error):
                raise IndexBuildError(
                    "Gemini credentials were rejected. Check GEMINI_API_KEY and try again."
                ) from error
            if not _is_temporary_error(error) or attempt == MAX_RETRIES - 1:
                status = _status_code(error)
                detail = f"HTTP {status}" if status else type(error).__name__
                raise IndexBuildError(f"Gemini embedding request failed ({detail}).") from error
            time.sleep(RETRY_DELAYS_SECONDS[attempt])

    raise AssertionError("The retry loop should always return or raise.")


def _read_index(path: Path) -> dict[str, Any]:
    try:
        raw_index = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise IndexValidationError(f"Vector index does not exist: {path.name}") from error
    except UnicodeDecodeError as error:
        raise IndexValidationError(f"Vector index is not valid UTF-8: {path.name}") from error
    except json.JSONDecodeError as error:
        raise IndexValidationError(
            f"Vector index contains invalid JSON: {path.name} "
            f"(line {error.lineno}, column {error.colno})"
        ) from error
    if not isinstance(raw_index, dict):
        raise IndexValidationError("Vector index root must be a JSON object.")
    return raw_index


def validate_index(index: dict[str, Any], knowledge_base: KnowledgeBase | None = None) -> int:
    """Validate index structure, dimensions, finite vector values, and source coverage."""

    required_root_fields = {
        "index_version", "embedding_model", "embedding_dimension", "record_count",
        "document_task_type", "query_task_type", "vectors",
    }
    missing = required_root_fields - index.keys()
    if missing:
        raise IndexValidationError(f"Vector index is missing fields: {', '.join(sorted(missing))}")
    if index["index_version"] != INDEX_VERSION:
        raise IndexValidationError("Vector index version is not supported by this builder.")
    if not isinstance(index["embedding_model"], str) or not index["embedding_model"].strip():
        raise IndexValidationError("Vector index embedding_model must be a non-empty string.")
    dimension = index["embedding_dimension"]
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension <= 0:
        raise IndexValidationError("Vector index embedding_dimension must be a positive integer.")
    if index["document_task_type"] != DOCUMENT_TASK_TYPE or index["query_task_type"] != QUERY_TASK_TYPE:
        raise IndexValidationError("Vector index has incompatible document/query embedding task types.")
    vectors = index["vectors"]
    if not isinstance(vectors, list) or not vectors:
        raise IndexValidationError("Vector index vectors must be a non-empty array.")
    if index["record_count"] != len(vectors):
        raise IndexValidationError("Vector index record_count does not match its vector array.")

    required_vector_fields = {
        "record_id", "category", "title", "source_section", "embedding",
        "content_fingerprint", "embedding_model", "index_version",
    }
    seen_ids: set[str] = set()
    for position, vector_record in enumerate(vectors, start=1):
        if not isinstance(vector_record, dict):
            raise IndexValidationError(f"Vector record {position} must be a JSON object.")
        missing_vector_fields = required_vector_fields - vector_record.keys()
        if missing_vector_fields:
            raise IndexValidationError(
                f"Vector record {position} is missing fields: {', '.join(sorted(missing_vector_fields))}"
            )
        record_id = vector_record["record_id"]
        if not isinstance(record_id, str) or not record_id.strip() or record_id in seen_ids:
            raise IndexValidationError(f"Vector record {position} has an invalid or duplicate record_id.")
        seen_ids.add(record_id)
        if vector_record["embedding_model"] != index["embedding_model"]:
            raise IndexValidationError(f"Vector record {record_id} uses a different embedding model.")
        if vector_record["index_version"] != INDEX_VERSION:
            raise IndexValidationError(f"Vector record {record_id} has an unsupported index version.")

        embedding = vector_record["embedding"]
        if not isinstance(embedding, list):
            raise IndexValidationError(f"Vector record {record_id} embedding must be an array.")
        try:
            values = np.asarray(embedding, dtype=np.float32)
        except (TypeError, ValueError) as error:
            raise IndexValidationError(f"Vector record {record_id} embedding contains invalid values.") from error
        if values.ndim != 1 or values.size != dimension or not np.isfinite(values).all():
            raise IndexValidationError(
                f"Vector record {record_id} does not have {dimension} finite embedding values."
            )

    if knowledge_base:
        source_records = {record.id: record for record in knowledge_base.records}
        if seen_ids != set(source_records):
            raise IndexValidationError("Vector index record IDs do not match the current knowledge base.")
        for vector_record in vectors:
            source = source_records[vector_record["record_id"]]
            if (
                vector_record["category"] != source.category
                or vector_record["title"] != source.title
                or vector_record["source_section"] != source.source_section
                or vector_record["content_fingerprint"] != content_fingerprint(source)
            ):
                raise IndexValidationError(
                    f"Vector record {source.id} does not match its current knowledge metadata."
                )
    return dimension


def _reusable_vectors(index_path: Path, model: str) -> dict[str, dict[str, Any]]:
    """Return only validated vectors whose model and source fingerprint still match."""

    if not index_path.is_file():
        return {}
    try:
        index = _read_index(index_path)
        validate_index(index)
    except IndexValidationError:
        return {}
    if index["embedding_model"] != model:
        return {}
    return {vector["record_id"]: vector for vector in index["vectors"]}


def _vector_record(record: KnowledgeRecord, embedding: list[float], model: str) -> dict[str, Any]:
    return {
        "record_id": record.id,
        "category": record.category,
        "title": record.title,
        "source_section": record.source_section,
        "embedding": embedding,
        "content_fingerprint": content_fingerprint(record),
        "embedding_model": model,
        "index_version": INDEX_VERSION,
    }


def _write_index_atomically(index: dict[str, Any], destination: Path) -> None:
    serialized = json.dumps(index, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    encoded = serialized.encode("utf-8")
    if len(encoded) > MAX_INDEX_BYTES:
        raise IndexBuildError(
            f"Vector index would be {len(encoded)} bytes, exceeding the {MAX_INDEX_BYTES}-byte bundle limit."
        )

    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.stem}-", suffix=".tmp", dir=destination.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def build_index(index_path: Path = INDEX_PATH, force: bool = False) -> tuple[int, int, int]:
    """Build a complete index, reusing unchanged validated vectors whenever possible."""

    if not settings.gemini_api_key_configured:
        raise IndexBuildError(
            "GEMINI_API_KEY is missing. Set it in the server environment or an ignored .env.local file."
        )

    knowledge_base = load_knowledge_base()
    model = settings.gemini_embedding_model
    reusable = {} if force else _reusable_vectors(index_path, model)
    client = genai.Client(api_key=settings.gemini_api_key)
    vectors: list[dict[str, Any]] = []
    reused_count = 0
    generated_count = 0

    for record in knowledge_base.records:
        existing = reusable.get(record.id)
        if existing and existing["content_fingerprint"] == content_fingerprint(record):
            vectors.append(existing)
            reused_count += 1
            continue
        vectors.append(_vector_record(record, embed_document(client, record, model), model))
        generated_count += 1

    dimensions = {len(vector["embedding"]) for vector in vectors}
    if len(dimensions) != 1:
        raise IndexBuildError("Gemini returned inconsistent embedding dimensions; the existing index was left unchanged.")
    dimension = dimensions.pop()
    index = {
        "index_version": INDEX_VERSION,
        "embedding_model": model,
        "embedding_dimension": dimension,
        "record_count": len(vectors),
        "document_task_type": DOCUMENT_TASK_TYPE,
        "query_task_type": QUERY_TASK_TYPE,
        "vectors": vectors,
    }
    validate_index(index, knowledge_base)
    _write_index_atomically(index, index_path)
    return len(vectors), dimension, reused_count + generated_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or validate the Ask Aman Gemini vector index.")
    parser.add_argument("--validate", action="store_true", help="Validate vectors.json without making Gemini requests.")
    parser.add_argument("--force", action="store_true", help="Regenerate every vector instead of reusing unchanged records.")
    args = parser.parse_args()

    try:
        knowledge_base = load_knowledge_base()
        if args.validate:
            dimension = validate_index(_read_index(INDEX_PATH), knowledge_base)
            print(
                f"Vector index validation passed: {len(knowledge_base.records)} records, dimension {dimension}."
            )
            return 0

        record_count, dimension, processed_count = build_index(force=args.force)
        print(
            f"Vector index build passed: {record_count} records, dimension {dimension}, "
            f"{processed_count} records generated or safely reused."
        )
        return 0
    except (IndexBuildError, IndexValidationError) as error:
        print(f"Index operation failed: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"Index operation failed: {type(error).__name__}.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
