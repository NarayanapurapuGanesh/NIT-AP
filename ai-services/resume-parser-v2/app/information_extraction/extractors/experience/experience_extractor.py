"""
Experience Extractor Engine.
Parses designation, organization, start/end dates, current job status, responsibilities, and location.
"""

import re
from typing import List
from app.information_extraction.normalizers.field_normalizers import DateNormalizer
from app.information_extraction.schemas.candidate_profile import ExperienceItem, ExtractedField
from app.resume_structure.schemas.semantic_resume import SectionNode, SemanticResumeModel
from core.logging import get_logger

logger = get_logger("experience_extractor")

DATE_RANGE_REGEX = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|[0-1]?\d)[a-z]*[\s,/-]*(\d{4})\b\s*[-–to]+\s*\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|[0-1]?\d)?[a-z]*[\s,/-]*(\d{4}|Present|Current)\b",
    re.IGNORECASE,
)


class ExperienceExtractor:
    """Professional & Academic Experience Extractor Engine."""

    def extract_experience(self, model: SemanticResumeModel) -> List[ExperienceItem]:
        experience_items: List[ExperienceItem] = []

        target_sections = [
            sec for sec in model.sections
            if sec.canonical_type in ["Professional Experience", "Academic Experience", "Industry Experience", "Research Experience", "Teaching Experience"]
        ]

        for sec in target_sections:
            blocks_text = sec.raw_text.split("\n\n")

            for b_text in blocks_text:
                lines = [l.strip() for l in b_text.split("\n") if l.strip()]
                if not lines:
                    continue

                desig_str = lines[0]
                org_str = lines[1] if len(lines) > 1 else ""
                resps = lines[2:] if len(lines) > 2 else []

                start_date_val = None
                end_date_val = None
                is_current = False

                match_dates = DATE_RANGE_REGEX.search(b_text)
                if match_dates:
                    raw_start = f"{match_dates.group(1)} {match_dates.group(2)}"
                    raw_end = match_dates.group(4)

                    start_date_val = ExtractedField(value=DateNormalizer.normalize_date(raw_start), raw_text=raw_start)
                    end_date_val = ExtractedField(value=DateNormalizer.normalize_date(raw_end), raw_text=raw_end)
                    if "present" in raw_end.lower() or "current" in raw_end.lower():
                        is_current = True

                item = ExperienceItem(
                    designation=ExtractedField(value=desig_str, raw_text=desig_str, normalized_value=desig_str, confidence=0.90, evidence=sec.evidence[:1]),
                    organization=ExtractedField(value=org_str, raw_text=org_str, normalized_value=org_str, confidence=0.88),
                    start_date=start_date_val or ExtractedField(),
                    end_date=end_date_val or ExtractedField(),
                    is_current=is_current,
                    responsibilities=resps,
                )
                experience_items.append(item)

        logger.debug("Experience extraction complete", items_count=len(experience_items))
        return experience_items
