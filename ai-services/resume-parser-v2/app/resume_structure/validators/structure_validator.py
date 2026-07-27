"""
Structural Validator Engine.
Evaluates structural quality score and checks for missing core sections or broken layout flow.
"""

from typing import List
from app.resume_structure.schemas.semantic_resume import SectionNode, StructureValidationResult
from core.logging import get_logger

logger = get_logger("structure_validator")

CORE_REQUIRED_SECTIONS = ["Education", "Skills", "Professional Experience", "Academic Experience", "Projects"]


class StructureValidatorEngine:
    """Structural Integrity & Validation Engine."""

    def validate_structure(
        self, sections: List[SectionNode], flow_warnings: List[str]
    ) -> StructureValidationResult:
        found_types = {sec.canonical_type for sec in sections}
        missing: List[str] = []

        # Check core requirements
        if not ("Education" in found_types or "Academic Experience" in found_types):
            missing.append("Education")
        if not ("Professional Experience" in found_types or "Academic Experience" in found_types or "Research Experience" in found_types):
            missing.append("Experience")
        if not ("Skills" in found_types or "Technical Skills" in found_types or "Programming Languages" in found_types):
            missing.append("Skills")

        # Deduplicate warnings
        duplicates = [w for w in flow_warnings if "Repeated section" in w]

        quality_score = 1.0
        if missing:
            quality_score -= len(missing) * 0.15
        if flow_warnings:
            quality_score -= len(flow_warnings) * 0.05

        quality_score = max(0.20, round(quality_score, 2))
        is_valid = quality_score >= 0.50

        result = StructureValidationResult(
            is_valid=is_valid,
            quality_score=quality_score,
            missing_sections=missing,
            duplicate_sections=duplicates,
            broken_flow_warnings=flow_warnings,
        )

        logger.info(
            "Structure validation completed",
            is_valid=is_valid,
            score=quality_score,
            missing_count=len(missing),
        )

        return result
