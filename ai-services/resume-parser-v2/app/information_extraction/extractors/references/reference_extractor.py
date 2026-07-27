"""
Reference Extractor Engine.
Parses academic/professional referee names, designations, institutions, emails, and phone numbers.
"""

import re
from typing import List
from app.information_extraction.schemas.candidate_profile import ExtractedField, ReferenceItem
from app.resume_structure.schemas.semantic_resume import SectionNode, SemanticResumeModel
from core.logging import get_logger

logger = get_logger("reference_extractor")

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


class ReferenceExtractor:
    """Academic Referees Extractor Engine."""

    def extract_references(self, model: SemanticResumeModel) -> List[ReferenceItem]:
        ref_items: List[ReferenceItem] = []

        target_sections = [
            sec for sec in model.sections if sec.canonical_type in ["References", "Referees"]
        ]

        for sec in target_sections:
            blocks = sec.raw_text.split("\n\n")

            for b in blocks:
                lines = [l.strip() for l in b.split("\n") if l.strip()]
                if not lines:
                    continue

                name_str = lines[0]
                desig_str = lines[1] if len(lines) > 1 else ""

                email_field = ExtractedField()
                match_e = EMAIL_REGEX.search(b)
                if match_e:
                    email_field = ExtractedField(value=match_e.group(0), raw_text=match_e.group(0), confidence=0.98)

                item = ReferenceItem(
                    referee_name=ExtractedField(value=name_str, raw_text=name_str, normalized_value=name_str, confidence=0.90, evidence=sec.evidence[:1]),
                    designation=ExtractedField(value=desig_str, raw_text=desig_str, normalized_value=desig_str, confidence=0.85),
                    email=email_field,
                )
                ref_items.append(item)

        logger.debug("Reference extraction complete", items_count=len(ref_items))
        return ref_items
