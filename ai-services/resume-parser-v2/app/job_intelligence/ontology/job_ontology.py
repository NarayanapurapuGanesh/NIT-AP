"""
Job Description Ontology & Taxonomy Resolver.
Normalizes academic ranks, degree requirements, departments, and skill terms.
"""

from typing import Tuple

ACADEMIC_RANKS = {
    "assistant professor": "Assistant Professor",
    "associate professor": "Associate Professor",
    "professor": "Professor",
    "adjunct faculty": "Adjunct Faculty",
    "research faculty": "Research Faculty",
    "visiting faculty": "Visiting Faculty",
    "guest faculty": "Guest Faculty",
    "postdoc": "Postdoctoral Researcher",
}


class JobOntologyResolver:
    """Ontology & Academic Rank Resolver."""

    @staticmethod
    def resolve_academic_rank(title_raw: str) -> str:
        clean = title_raw.strip().lower()
        for key, canonical in ACADEMIC_RANKS.items():
            if key in clean:
                return canonical
        return "Assistant Professor"

    @staticmethod
    def is_phd_required(text_raw: str) -> bool:
        clean = text_raw.lower()
        if "ph.d" in clean or "phd" in clean or "doctorate" in clean:
            return True
        return False
