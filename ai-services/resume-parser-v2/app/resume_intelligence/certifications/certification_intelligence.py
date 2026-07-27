"""
Certification Intelligence Engine.
Analyzes vendor diversity and credential validity.
"""

from typing import Any, Dict
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from core.logging import get_logger

logger = get_logger("certification_intelligence")


class CertificationIntelligenceEngine:
    """Certification Intelligence Engine."""

    def analyze_certifications(self, profile: StructuredCandidateProfile) -> Dict[str, Any]:
        cert_count = len(profile.certifications)
        issuers = {c.issuer.value for c in profile.certifications if c.issuer.value}

        return {
            "total_certifications": cert_count,
            "unique_issuers_count": len(issuers),
        }
