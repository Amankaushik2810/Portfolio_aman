"""Validation rules for deterministic public links in Ask Aman knowledge."""

from __future__ import annotations

import re
from urllib.parse import urlparse


APPROVED_EXTERNAL_DOMAINS = frozenset({"play.google.com", "github.com", "linkedin.com"})
SUPPORTED_LINK_TYPES = frozenset({"play_store", "github", "linkedin", "live_demo"})
_LINK_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def public_link_error(link_id: object, label: object, url: object, link_type: object) -> str | None:
    """Return a safe validation message, never performing network access."""

    if not isinstance(link_id, str) or not _LINK_ID_PATTERN.fullmatch(link_id):
        return "link id must be a stable lowercase hyphenated identifier"
    if not isinstance(label, str) or not label.strip():
        return "link label must be a non-empty string"
    if link_type not in SUPPORTED_LINK_TYPES:
        return "link type is not supported"
    if not isinstance(url, str) or not url.strip():
        return "link URL must be a non-empty string"

    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        return "link URL must be a valid HTTPS URL"
    hostname = (parsed.hostname or "").lower()
    if hostname not in APPROVED_EXTERNAL_DOMAINS:
        return "link URL domain is not approved"
    return None
