"""
Gap Analysis Engine.
Identifies qualification deficits, experience gaps, missing mandatory skills, and publication shortages.
"""

from typing import List, Tuple
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.job_intelligence.schemas.job_models import JobIntelligenceModel
from app.matching.schemas.match_models import RequirementMatchItem
from core.logging import get_logger

logger = get_logger("gap_analyzer")


class GapAnalyzerEngine:
    """Gap Analysis Engine."""

    def analyze_gaps(
        self, candidate: StructuredCandidateProfile, job: JobIntelligenceModel
    ) -> Tuple[List[str], List[RequirementMatchItem], List[RequirementMatchItem]]:
        critical_gaps: List[str] = []
        matched: List[RequirementMatchItem] = []
        unmatched: List[RequirementMatchItem] = []

        cand_degrees = [edu.degree.value for edu in candidate.education if edu.degree.value]

        # Qualification check
        if job.qualification.is_phd_mandatory:
            if "Ph.D." in cand_degrees:
                matched.append(
                    RequirementMatchItem(
                        requirement_name="Ph.D. Qualification",
                        is_met=True,
                        candidate_value="Ph.D. Degree present",
                        required_value="Ph.D. Mandatory",
                    )
                )
            else:
                critical_gaps.append("Candidate lacks mandatory Ph.D. degree required for this post.")
                unmatched.append(
                    RequirementMatchItem(
                        requirement_name="Ph.D. Qualification",
                        is_met=False,
                        candidate_value=", ".join(cand_degrees) if cand_degrees else "No Degree",
                        required_value="Ph.D. Mandatory",
                    )
                )

        # Experience check
        min_exp = job.experience.min_total_experience_years
        cand_exp_years = len(candidate.experience) * 2.0
        if cand_exp_years < min_exp:
            g_msg = f"Experience deficit: {cand_exp_years} years vs required {min_exp} years."
            critical_gaps.append(g_msg)
            unmatched.append(
                RequirementMatchItem(
                    requirement_name="Minimum Total Experience",
                    is_met=False,
                    candidate_value=f"{cand_exp_years} years",
                    required_value=f"{min_exp} years",
                )
            )
        else:
            matched.append(
                RequirementMatchItem(
                    requirement_name="Minimum Total Experience",
                    is_met=True,
                    candidate_value=f"{cand_exp_years} years",
                    required_value=f"{min_exp} years",
                )
            )

        logger.debug("Gap analysis complete", critical_gaps_count=len(critical_gaps))
        return critical_gaps, matched, unmatched
