"""Load and validate the public Ask Aman knowledge base in memory."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from api.errors import KnowledgeLoadError
from api.models import KnowledgeRecord


KNOWLEDGE_DIRECTORY = Path(__file__).resolve().parent.parent / "rag_data"
KNOWLEDGE_FILES = {
    "about": "about.json",
    "education": "education.json",
    "skills": "skills.json",
    "projects": "projects.json",
    "experience": "experience.json",
    "contact": "contact.json",
    "faq": "faq.json",
}


@dataclass(frozen=True)
class KnowledgeBase:
    """Validated records and metadata retained for the serverless process lifetime."""

    records: tuple[KnowledgeRecord, ...]
    category_counts: dict[str, int]


def _load_file(path: Path, expected_category: str) -> list[KnowledgeRecord]:
    try:
        raw_data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise KnowledgeLoadError(f"Required knowledge file is missing: {path.name}") from error
    except UnicodeDecodeError as error:
        raise KnowledgeLoadError(f"Knowledge file is not valid UTF-8: {path.name}") from error
    except json.JSONDecodeError as error:
        raise KnowledgeLoadError(
            f"Knowledge file contains invalid JSON: {path.name} "
            f"(line {error.lineno}, column {error.colno})"
        ) from error

    if not isinstance(raw_data, list):
        raise KnowledgeLoadError(f"Knowledge file must contain a JSON array: {path.name}")
    if not raw_data:
        raise KnowledgeLoadError(f"Knowledge file must contain at least one record: {path.name}")

    records: list[KnowledgeRecord] = []
    for record_number, raw_record in enumerate(raw_data, start=1):
        try:
            record = KnowledgeRecord.model_validate(raw_record)
        except ValidationError as error:
            details = "; ".join(
                f"{'.'.join(str(part) for part in issue['loc'])}: {issue['msg']}"
                for issue in error.errors()
            )
            raise KnowledgeLoadError(
                f"Invalid record {record_number} in {path.name}: {details}"
            ) from error

        if record.category != expected_category:
            raise KnowledgeLoadError(
                f"Invalid record {record_number} in {path.name}: category must be "
                f"'{expected_category}', got '{record.category}'"
            )
        records.append(record)

    return records


def load_knowledge_base(data_directory: Path | None = None) -> KnowledgeBase:
    """Read every required knowledge file and reject malformed or duplicate records."""

    directory = data_directory or KNOWLEDGE_DIRECTORY
    if not directory.is_dir():
        raise KnowledgeLoadError(f"Knowledge directory does not exist: {directory}")

    records: list[KnowledgeRecord] = []
    seen_ids: set[str] = set()
    seen_link_ids: set[str] = set()
    for expected_category, file_name in KNOWLEDGE_FILES.items():
        for record in _load_file(directory / file_name, expected_category):
            if record.id in seen_ids:
                raise KnowledgeLoadError(f"Duplicate knowledge record id: {record.id}")
            seen_ids.add(record.id)
            for link in record.links:
                if link.id in seen_link_ids:
                    raise KnowledgeLoadError(f"Duplicate public link id: {link.id}")
                seen_link_ids.add(link.id)
            records.append(record)

    category_counts = dict(sorted(Counter(record.category for record in records).items()))
    return KnowledgeBase(records=tuple(records), category_counts=category_counts)
