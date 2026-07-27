"""
Shared utilities for timing, formatting, and string manipulation.
"""

from datetime import datetime, timezone
import hashlib


def generate_content_hash(content: bytes) -> str:
    """Generates a SHA-256 hex digest for document deduplication and verification."""
    return hashlib.sha256(content).hexdigest()


def get_utc_now() -> datetime:
    """Returns current UTC timestamp with timezone information."""
    return datetime.now(timezone.utc)
