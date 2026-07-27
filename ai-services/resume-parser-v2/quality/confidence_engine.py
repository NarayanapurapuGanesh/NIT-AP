"""
Confidence Engine Module (Module 12) — v3.0 Layout-Aware Engine.

Calculates itemized confidence scores for each extracted attribute in the Enterprise Candidate Profile.
v3.0 adds layout structure penalties (missing sections, failed column detection, label artifact noise)
to ensure low-confidence resumes correctly trigger LLM callback fallback.
"""

from typing import Any, Dict, Optional
from schemas.enterprise_profile import FieldConfidenceScores
from extractors.deterministic_extractor import DeterministicEntities


class ConfidenceEngine:
    """Calculates weighted confidence scores based on validation regex, layout quality, and entity completeness."""

    def compute_confidence(
        self, entities: DeterministicEntities, layout_structure: Optional[Any] = None
    ) -> FieldConfidenceScores:
        # Email confidence
        email_score = 1.0 if (entities.email and "@" in entities.email and "." in entities.email) else 0.0

        # Phone confidence
        phone_score = 1.0 if (entities.phone and len(re_clean_digits(entities.phone)) >= 10) else 0.0

        # Name confidence
        name_score = 0.99 if (entities.name and len(entities.name.split()) >= 2) else (0.50 if entities.name else 0.0)

        # Skills confidence
        skills_score = min(0.98, 0.70 + (len(entities.skills) * 0.03)) if entities.skills else 0.0

        # Education confidence
        edu_score = 0.95 if (entities.education and any(e.degree for e in entities.education)) else 0.0

        # Experience confidence
        exp_score = 0.90 if (entities.experience and any(e.title for e in entities.experience)) else 0.0

        # Publications confidence (0.0 if not present, optional field)
        pub_score = 0.96 if entities.publications else 0.0

        # Projects confidence (penalized if titles contain label noise or lack descriptions)
        proj_score = 0.0
        if entities.projects:
            proj_score = 0.88
            has_label_noise = any("PROJECT TITLE" in p.title.upper() or "PROJECT:" in p.title.upper() for p in entities.projects)
            has_descriptions = any(p.description and len(p.description) > len(p.title) + 5 for p in entities.projects)
            if has_label_noise:
                proj_score -= 0.25
            if not has_descriptions:
                proj_score -= 0.15

        # v3.0: Profile summary confidence
        profile_summary_score = 0.0
        if entities.profile_summary:
            word_count = len(entities.profile_summary.split())
            if word_count >= 20:
                profile_summary_score = 0.95
            elif word_count >= 10:
                profile_summary_score = 0.85
            elif word_count >= 3:
                profile_summary_score = 0.70

        # v3.0: Soft skills confidence
        soft_skills_score = 0.0
        if entities.soft_skills:
            soft_skills_score = min(0.95, 0.70 + (len(entities.soft_skills) * 0.05))

        # v3.0: Address confidence
        address_score = 0.0
        if entities.address:
            address_score = 0.90 if len(entities.address) > 5 else 0.70

        # --- Completeness & Layout Quality Penalty Calculation ---
        layout_penalty = 0.0
        if layout_structure:
            sections_found = len(getattr(layout_structure, "sections", []))
            is_two_col = getattr(layout_structure, "is_two_column", False)

            if sections_found == 0:
                layout_penalty += 20.0
            elif sections_found < 2:
                layout_penalty += 10.0

        # Core fields expected in a complete resume evaluation
        core_scores = [name_score, email_score, phone_score, skills_score, edu_score, exp_score]
        
        # Penalize if critical core sections are missing
        missing_core_count = sum(1 for s in core_scores if s == 0.0)
        completeness_penalty = missing_core_count * 6.0

        # Calculate overall weighted average
        all_present = [s for s in [name_score, email_score, phone_score, skills_score, edu_score, exp_score, profile_summary_score, proj_score, pub_score, soft_skills_score, address_score] if s > 0]
        raw_avg = (sum(all_present) / len(all_present)) * 100.0 if all_present else 0.0

        # Final overall average factors in completeness penalty and layout penalty
        final_overall = max(10.0, min(100.0, raw_avg - layout_penalty - completeness_penalty))

        return FieldConfidenceScores(
            name=round(name_score * 100, 1),
            email=round(email_score * 100, 1),
            phone=round(phone_score * 100, 1),
            skills=round(skills_score * 100, 1),
            education=round(edu_score * 100, 1),
            experience=round(exp_score * 100, 1),
            publications=round(pub_score * 100, 1),
            projects=round(max(0.0, proj_score) * 100, 1),
            profile_summary=round(profile_summary_score * 100, 1),
            soft_skills=round(soft_skills_score * 100, 1),
            address=round(address_score * 100, 1),
            overall_average=round(final_overall, 1),
        )


def re_clean_digits(phone_str: str) -> str:
    import re
    return re.sub(r'\D', '', phone_str)

