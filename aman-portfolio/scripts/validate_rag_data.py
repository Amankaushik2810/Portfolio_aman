"""Validate the Ask Aman JSON knowledge base without external dependencies."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
if str(PROJECT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIRECTORY))

from api.link_validation import public_link_error


REQUIRED_FIELDS = {"id", "category", "title", "content", "keywords", "source_section"}
VALID_CATEGORIES = {"about", "education", "skills", "projects", "experience", "contact", "faq"}
DATA_FILES = {category: f"{category}.json" for category in VALID_CATEGORIES}


def validate_record(
    record: object,
    file_name: str,
    index: int,
    seen_ids: set[str],
    seen_link_ids: set[str] | None = None,
) -> list[str]:
    location = f"{file_name}[{index}]"
    if not isinstance(record, dict):
        return [f"{location}: record must be a JSON object"]

    errors = []
    missing = REQUIRED_FIELDS - record.keys()
    if missing:
        errors.append(f"{location}: missing required fields: {', '.join(sorted(missing))}")

    for field in ("id", "category", "title", "content", "source_section"):
        if field in record and (not isinstance(record[field], str) or not record[field].strip()):
            errors.append(f"{location}: {field} must be a non-empty string")

    record_id = record.get("id")
    if isinstance(record_id, str) and record_id.strip():
        if record_id in seen_ids:
            errors.append(f"{location}: duplicate id: {record_id}")
        seen_ids.add(record_id)

    category = record.get("category")
    if category not in VALID_CATEGORIES:
        errors.append(f"{location}: invalid category: {category!r}")
    elif category != Path(file_name).stem:
        errors.append(f"{location}: category must match its file name")

    keywords = record.get("keywords")
    if not isinstance(keywords, list) or not keywords or any(not isinstance(keyword, str) or not keyword.strip() for keyword in keywords):
        errors.append(f"{location}: keywords must be a non-empty array of non-empty strings")

    links = record.get("links", [])
    if links is None or not isinstance(links, list):
        errors.append(f"{location}: links must be an array when provided")
    else:
        seen_link_ids = seen_link_ids if seen_link_ids is not None else set()
        for link_index, link in enumerate(links):
            link_location = f"{location}.links[{link_index}]"
            if not isinstance(link, dict):
                errors.append(f"{link_location}: link must be a JSON object")
                continue
            missing_link_fields = {"id", "label", "url", "type"} - link.keys()
            if missing_link_fields:
                errors.append(f"{link_location}: missing fields: {', '.join(sorted(missing_link_fields))}")
                continue
            link_error = public_link_error(link["id"], link["label"], link["url"], link["type"])
            if link_error:
                errors.append(f"{link_location}: {link_error}")
                continue
            if link["id"] in seen_link_ids:
                errors.append(f"{link_location}: duplicate link id: {link['id']}")
                continue
            seen_link_ids.add(link["id"])

    return errors


def main() -> int:
    data_dir = Path(__file__).resolve().parent.parent / "rag_data"
    errors: list[str] = []
    seen_ids: set[str] = set()
    seen_link_ids: set[str] = set()
    record_count = 0

    for category, file_name in sorted(DATA_FILES.items()):
        path = data_dir / file_name
        if not path.is_file():
            errors.append(f"{file_name}: required knowledge file is missing")
            continue

        try:
            with path.open(encoding="utf-8") as handle:
                records = json.load(handle)
        except json.JSONDecodeError as error:
            errors.append(f"{file_name}: invalid JSON ({error.msg} at line {error.lineno}, column {error.colno})")
            continue

        if not isinstance(records, list):
            errors.append(f"{file_name}: root value must be a JSON array")
            continue

        if not records:
            errors.append(f"{file_name}: must contain at least one record")
            continue

        for index, record in enumerate(records):
            errors.extend(validate_record(record, file_name, index, seen_ids, seen_link_ids))
            record_count += 1

    if errors:
        print("RAG knowledge-base validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    print(f"RAG knowledge-base validation passed: {record_count} records across {len(DATA_FILES)} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
