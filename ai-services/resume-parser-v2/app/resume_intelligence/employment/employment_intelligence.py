"""
Employment Intelligence Engine.
Analyzes career progression, role promotion, and employer stability.
"""

from typing import Any, Dict
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from core.logging import get_logger

logger = get_logger("employment_intelligence")


class EmploymentIntelligenceEngine:
    """Employment Intelligence Engine."""

    def analyze_employment(self, profile: StructuredCandidateProfile) -> Dict[str, Any]:
        exp_count = len(profile.experience)
        organizations = [exp.organization.value for exp in profile.experience if exp.organization.value]

        return {
            "total_roles": exp_count,
            "unique_employers": len(set(organizations)),
            "is_stable": exp_count <= 6,
        }
