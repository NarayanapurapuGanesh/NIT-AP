"""
Award Extractor Engine.
Parses award title, organization, year, and description.
"""

from typing import List
from app.information_extraction.schemas.candidate_profile import AwardItem, ExtractedField
from app.resume_structure.schemas.semantic_resume import SectionNode, SemanticResumeModel
from core.logging import get_logger

logger = get_logger("award_extractor")


class AwardExtractor:
    """Awards & Honors Extractor Engine."""

    def extract_awards(self, model: SemanticResumeModel) -> List[AwardItem]:
        award_items: List[AwardItem] = []

        target_sections = [
            sec for sec in model.sections
            if sec.canonical_type in ["Awards", "Achievements", "Honors"]
        ]

        for sec in target_sections:
            lines = [l.strip() for l in sec.raw_text.split("\n") if l.strip()]
            for line in lines:
                if len(line) < 5:
                    continue
                item = AwardItem(
                    award_title=ExtractedField(value=line, raw_text=line, normalized_value=line, confidence=0.88, evidence=sec.evidence[:1])
                )
                award_items.append(item)

        logger.debug("Award extraction complete", items_count=len(award_items))
        return award_items
