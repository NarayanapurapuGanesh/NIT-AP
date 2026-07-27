"""
Heading Intelligence Engine.
Determines heading depth level (H1, H2, H3), alias resolution, confidence scoring, and case normalization.
"""

from app.resume_structure.heading_classifier.heading_classifier import ClassifiedHeading
from app.resume_structure.schemas.semantic_resume import HeadingIntelligence
from core.logging import get_logger

logger = get_logger("heading_intelligence")


class HeadingIntelligenceEngine:
    """Heading Intelligence Evaluator."""

    def evaluate_heading_intelligence(self, classified: ClassifiedHeading) -> HeadingIntelligence:
        # Determine Heading Level (H1 vs H2 vs H3)
        # H1: Primary section categories (Education, Professional Experience, Publications)
        # H2: Sub-sections (Teaching Experience under Academic Experience, Journal Papers under Publications)
        # H3: Granular sub-headings (Technical Skills under Skills)

        h_level = 1
        if classified.canonical_type in ["Technical Skills", "Soft Skills", "Programming Languages", "Tools", "Frameworks"]:
            h_level = 2
        elif classified.canonical_type in ["Journal Papers", "Conference Proceedings", "Book Chapters"]:
            h_level = 2

        intelligence = HeadingIntelligence(
            canonical_type=classified.canonical_type,
            original_heading=classified.candidate.raw_text,
            heading_level=h_level,
            confidence=classified.confidence,
            is_misspelled=classified.is_misspelled,
            alias_matched=classified.matched_alias,
        )

        logger.debug(
            "Heading intelligence evaluated",
            canonical=classified.canonical_type,
            level=h_level,
            confidence=classified.confidence,
        )

        return intelligence
