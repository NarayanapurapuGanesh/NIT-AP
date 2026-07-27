"""
Field Normalizer Utilities for Name, Date, Phone, Email, URLs, and Degrees.
"""

import re
from typing import Tuple

PREFIX_TITLES = {"dr.", "prof.", "mr.", "ms.", "mrs.", "dr", "prof"}
DEGREE_CANONICAL_MAP = {
    "b.tech": "B.Tech",
    "btech": "B.Tech",
    "b.e": "B.E.",
    "be": "B.E.",
    "m.tech": "M.Tech",
    "mtech": "M.Tech",
    "m.s": "M.S.",
    "ms": "M.S.",
    "b.s": "B.S.",
    "bs": "B.S.",
    "ph.d": "Ph.D.",
    "phd": "Ph.D.",
    "b.sc": "B.Sc.",
    "m.sc": "M.Sc.",
    "m.ba": "M.B.A.",
    "mba": "M.B.A.",
}


class NameNormalizer:
    @staticmethod
    def normalize_name(raw_name: str) -> Tuple[str, str, str, str]:
        parts = [p.strip() for p in raw_name.split() if p.strip()]
        if not parts:
            return "", "", "", ""

        if parts[0].lower() in PREFIX_TITLES:
            parts = parts[1:]

        if not parts:
            return raw_name.strip(), "", "", ""

        full = " ".join(parts)
        first = parts[0]
        last = parts[-1] if len(parts) > 1 else ""
        middle = " ".join(parts[1:-1]) if len(parts) > 2 else ""

        return full, first, middle, last


class ContactNormalizer:
    @staticmethod
    def normalize_email(email_str: str) -> str:
        return email_str.strip().lower()

    @staticmethod
    def normalize_phone(phone_str: str) -> str:
        digits = re.sub(r"[^\d+]", "", phone_str)
        if len(digits) == 10 and not digits.startswith("+"):
            return f"+91-{digits}"
        return digits

    @staticmethod
    def normalize_url(url_str: str) -> str:
        clean = url_str.strip()
        if not clean.startswith("http://") and not clean.startswith("https://"):
            return f"https://{clean}"
        return clean


class DateNormalizer:
    @staticmethod
    def normalize_date(date_str: str) -> str:
        clean = date_str.strip()
        if clean.lower() in ["present", "current", "till date", "now"]:
            return "Present"

        # Regex for Year (e.g., 2020)
        match_year = re.search(r"\b(19\d\d|20\d\d)\b", clean)
        year = match_year.group(1) if match_year else ""

        # Check month
        months = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
            "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
        }
        month = "01"
        for m_name, m_num in months.items():
            if m_name in clean.lower():
                month = m_num
                break

        if year:
            return f"{year}-{month}"
        return clean


class DegreeNormalizer:
    @staticmethod
    def normalize_degree(degree_str: str) -> str:
        clean = degree_str.strip().lower()
        for key, canonical in DEGREE_CANONICAL_MAP.items():
            if key in clean:
                return canonical
        return degree_str.strip().title()
