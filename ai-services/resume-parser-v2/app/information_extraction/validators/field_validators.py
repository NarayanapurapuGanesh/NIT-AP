"""
Validator Utilities for Contact info, URLs, CGPA bounds, and Entity Deduplication.
"""

import re
from typing import List, TypeVar

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
URL_REGEX = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)

T = TypeVar("T")


class FieldValidator:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        return bool(EMAIL_REGEX.match(email.strip()))

    @staticmethod
    def is_valid_url(url: str) -> bool:
        return bool(URL_REGEX.match(url.strip()))

    @staticmethod
    def is_valid_cgpa(cgpa: float) -> bool:
        return 0.0 <= cgpa <= 10.0

    @staticmethod
    def is_valid_percentage(percentage: float) -> bool:
        return 0.0 <= percentage <= 100.0

    @staticmethod
    def deduplicate_entities(items: List[str]) -> List[str]:
        seen = set()
        deduped = []
        for item in items:
            clean = item.strip()
            if clean.lower() not in seen:
                seen.add(clean.lower())
                deduped.append(clean)
        return deduped
