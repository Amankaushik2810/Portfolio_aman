"""Domain-specific errors for the Ask Aman backend."""


class KnowledgeLoadError(RuntimeError):
    """Raised when the local knowledge base cannot be loaded safely."""
