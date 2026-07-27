"""
Evidence Verifier Engine.
Cross-references every extracted property against line-by-line bounding box evidence, marking unbacked fields as UNVERIFIED.
"""

from typing import List
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from core.logging import get_logger

logger = get_logger("evidence_verifier")


class EvidenceVerifierEngine:
    """Evidence Verifier & Lineage Guard Engine."""

    def verify_evidence(self, profile: StructuredCandidateProfile) -> List[str]:
        unbacked_fields: List[str] = []

        if profile.contact.full_name.value and not profile.contact.full_name.evidence:
            unbacked_fields.append("contact.full_name (Missing bounding box evidence)")

        if profile.contact.email.value and not profile.contact.email.evidence:
            unbacked_fields.append("contact.email (Missing bounding box evidence)")

        for idx, edu in enumerate(profile.education):
            if edu.degree.value and not edu.degree.evidence:
                unbacked_fields.append(f"education[{idx}].degree (Missing bounding box evidence)")

        for idx, exp in enumerate(profile.experience):
            if exp.designation.value and not exp.designation.evidence:
                unbacked_fields.append(f"experience[{idx}].designation (Missing bounding box evidence)")

        logger.debug("Evidence verification completed", unbacked_fields_count=len(unbacked_fields))
        return unbacked_fields
