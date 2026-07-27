"""
Missing Information Detection Module (Module 9) — v3.0.

Evaluates candidate profile completeness and highlights missing fields:
- Missing contact details (Phone, Email, LinkedIn, Address)
- Missing experience dates or job responsibilities
- Missing education graduation years or degrees
- Missing profile summary
- Missing soft skills
- Generates actionable profile improvement suggestions.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from extractors.deterministic_extractor import DeterministicEntities
from extractors.link_discovery import ProfileLinks


class MissingFieldNotice(BaseModel):
    field_name: str = Field(..., description="Field name missing or incomplete")
    severity: str = Field("WARNING", description="CRITICAL, WARNING, INFO")
    suggestion: str = Field(..., description="Actionable suggestion for candidate or recruiter")


class QualityEvaluationReport(BaseModel):
    completeness_score: float = Field(..., description="Profile completeness percentage [0 - 100%]")
    missing_fields: List[MissingFieldNotice] = Field(default_factory=list, description="Missing items")
    improvement_recommendations: List[str] = Field(default_factory=list, description="Suggested profile enhancements")


class MissingInformationEvaluator:
    """Evaluator analyzing candidate profile completeness and data quality gaps."""

    def evaluate_completeness(
        self,
        entities: DeterministicEntities,
        links: ProfileLinks
    ) -> QualityEvaluationReport:
        missing: List[MissingFieldNotice] = []
        recommendations: List[str] = []
        total_weight = 100
        score = 100

        # 1. Contact Information Checks
        if not entities.email:
            score -= 20
            missing.append(
                MissingFieldNotice(
                    field_name="Email Address",
                    severity="CRITICAL",
                    suggestion="Email address is missing or invalid. Add a valid contact email address.",
                )
            )

        if not entities.phone:
            score -= 15
            missing.append(
                MissingFieldNotice(
                    field_name="Phone Number",
                    severity="WARNING",
                    suggestion="Phone number is missing. Include a primary telephone contact number.",
                )
            )
            recommendations.append("Provide a direct phone contact number for interview scheduling.")

        if not links.linkedin:
            score -= 10
            missing.append(
                MissingFieldNotice(
                    field_name="LinkedIn Profile Link",
                    severity="WARNING",
                    suggestion="LinkedIn profile URL was not found in the document.",
                )
            )
            recommendations.append("Add LinkedIn profile URL to enable instant professional background verification.")

        # v3.0: Address check
        if not entities.address:
            score -= 3
            missing.append(
                MissingFieldNotice(
                    field_name="Address / Location",
                    severity="INFO",
                    suggestion="No city or locality information was found. Include location for geographic preference matching.",
                )
            )

        # v3.0: Profile Summary check
        if not entities.profile_summary:
            score -= 5
            missing.append(
                MissingFieldNotice(
                    field_name="Profile Summary / Objective",
                    severity="INFO",
                    suggestion="No profile summary or career objective section was detected. Consider adding a brief professional overview.",
                )
            )
            recommendations.append("Add a profile summary or career objective section to strengthen first impression.")

        # 2. Education Checks
        if not entities.education:
            score -= 20
            missing.append(
                MissingFieldNotice(
                    field_name="Education Records",
                    severity="CRITICAL",
                    suggestion="No degree or education record could be identified.",
                )
            )
        else:
            for edu in entities.education:
                if not edu.year:
                    score -= 5
                    missing.append(
                        MissingFieldNotice(
                            field_name=f"Graduation Year ({edu.degree})",
                            severity="INFO",
                            suggestion=f"Graduation year missing for degree '{edu.degree}'.",
                        )
                    )
                    break

        # 3. Work Experience Dates Check
        if not entities.experience:
            score -= 15
            missing.append(
                MissingFieldNotice(
                    field_name="Work Experience",
                    severity="WARNING",
                    suggestion="Work experience / employment section is empty.",
                )
            )
        else:
            dates_missing = [e for e in entities.experience if not e.start_date]
            if dates_missing:
                score -= 10
                missing.append(
                    MissingFieldNotice(
                        field_name="Experience Dates",
                        severity="WARNING",
                        suggestion=f"Dates missing for {len(dates_missing)} experience entry/entries.",
                    )
                )
                recommendations.append("Ensure start and end years are explicitly specified for all work experience entries.")

        # v3.0: Soft Skills check
        if not entities.soft_skills:
            score -= 3
            missing.append(
                MissingFieldNotice(
                    field_name="Soft Skills",
                    severity="INFO",
                    suggestion="No soft skills or interpersonal skills were detected. Consider adding teamwork, communication, or leadership skills.",
                )
            )

        # 4. Academic CV specific link checks
        if entities.publications and not links.google_scholar and not links.orcid:
            recommendations.append("Include Google Scholar or ORCID profile link to verify publication citations automatically.")

        final_score = max(0, min(100, score))

        return QualityEvaluationReport(
            completeness_score=float(final_score),
            missing_fields=missing,
            improvement_recommendations=recommendations,
        )
