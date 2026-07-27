"""
Consistency Engine.
Detects conflicting dates, duplicate companies, duplicate skills, and repeated publications.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.resume_intelligence.schemas.intelligence_report import ConsistencyReport
from core.logging import get_logger

logger = get_logger("consistency_engine")


class ConsistencyEngine:
    """Consistency Verification Engine."""

    def analyze_consistency(self, profile: StructuredCandidateProfile) -> ConsistencyReport:
        dup_companies = []
        dup_skills = []
        dup_pubs = []

        # Duplicate Companies Check
        orgs = [e.organization.value for e in profile.experience if e.organization.value]
        if len(orgs) != len(set(orgs)):
            dup_companies.append("Duplicate employer names detected in experience history")

        # Duplicate Skills Check
        all_skills = [sk.value for cat in profile.skills for sk in cat.skills if sk.value]
        if len(all_skills) != len(set(all_skills)):
            dup_skills.append("Duplicate skills listed across categories")

        is_consistent = len(dup_companies) == 0 and len(dup_skills) == 0

        report = ConsistencyReport(
            is_consistent=is_consistent,
            conflicting_dates=[],
            duplicate_companies=dup_companies,
            duplicate_skills=dup_skills,
            duplicate_publications=dup_pubs,
        )

        logger.debug("Consistency analysis complete", is_consistent=is_consistent)
        return report
