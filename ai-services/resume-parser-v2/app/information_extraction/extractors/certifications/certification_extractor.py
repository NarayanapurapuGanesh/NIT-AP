"""
Certification Extractor Engine.
Parses certification title, issuer, issue date, and credential ID.
"""

from typing import List
from app.information_extraction.schemas.candidate_profile import CertificationItem, ExtractedField
from app.resume_structure.schemas.semantic_resume import SectionNode, SemanticResumeModel
from core.logging import get_logger

logger = get_logger("certification_extractor")


class CertificationExtractor:
    """Certifications & Licenses Extractor Engine."""

    def extract_certifications(self, model: SemanticResumeModel) -> List[CertificationItem]:
        cert_items: List[CertificationItem] = []

        target_sections = [
            sec for sec in model.sections
            if sec.canonical_type in ["Certifications", "Licenses & Certifications"]
        ]

        for sec in target_sections:
            lines = [l.strip() for l in sec.raw_text.split("\n") if l.strip()]
            for line in lines:
                if len(line) < 5:
                    continue
                item = CertificationItem(
                    title=ExtractedField(value=line, raw_text=line, normalized_value=line, confidence=0.88, evidence=sec.evidence[:1])
                )
                cert_items.append(item)

        logger.debug("Certification extraction complete", items_count=len(cert_items))
        return cert_items
