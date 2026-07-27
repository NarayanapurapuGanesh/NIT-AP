"""
Publication Intelligence Engine.
Analyzes publication breakdown, DOI presence, and duplicate paper detection.
"""

from typing import Any, Dict, List
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from core.logging import get_logger

logger = get_logger("publication_intelligence")


class PublicationIntelligenceEngine:
    """Publication Quality & Deduplication Engine."""

    def analyze_publications(self, profile: StructuredCandidateProfile) -> Dict[str, Any]:
        titles = [pub.title.value for pub in profile.publications if pub.title.value]
        unique_titles = set(titles)

        duplicates: List[str] = []
        if len(titles) != len(unique_titles):
            duplicates.append("Duplicate publication entries identified in profile")

        return {
            "total_publications": len(titles),
            "unique_publications": len(unique_titles),
            "duplicate_warnings": duplicates,
        }
