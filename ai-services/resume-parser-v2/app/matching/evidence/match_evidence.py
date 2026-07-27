"""
Match Evidence Engine.
Attaches evidence IDs and field citations to candidate match decisions.
"""

from typing import List
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.matching.schemas.match_models import MatchEvidenceItem
from core.logging import get_logger

logger = get_logger("match_evidence")


class MatchEvidenceEngine:
    """Match Evidence Engine."""

    def build_evidence(self, candidate: StructuredCandidateProfile) -> List[MatchEvidenceItem]:
        evidence_items: List[MatchEvidenceItem] = []

        if candidate.contact.full_name.value:
            evidence_items.append(
                MatchEvidenceItem(
                    source_field="contact.full_name",
                    extracted_text=candidate.contact.full_name.value,
                    rule_id="name_matching",
                )
            )

        for edu in candidate.education:
            if edu.degree.value:
                evidence_items.append(
                    MatchEvidenceItem(
                        source_field="education.degree",
                        extracted_text=edu.degree.value,
                        rule_id="degree_matching",
                    )
                )

        logger.debug("Match evidence items generated", count=len(evidence_items))
        return evidence_items
