"""
Profile Validator Engine.
Validates profile completeness, required fields, and contact information.
"""

from typing import List, Tuple
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from core.logging import get_logger

logger = get_logger("profile_validator")


class ProfileValidatorEngine:
    """Profile Validation Engine."""

    def validate_profile(self, profile: StructuredCandidateProfile) -> Tuple[List[str], List[str]]:
        warnings: List[str] = []
        errors: List[str] = []

        if not profile.contact.full_name.value:
            errors.append("Missing candidate full name in contact header.")

        if not profile.contact.email.value:
            warnings.append("Missing contact email address.")

        if not profile.contact.phone.value:
            warnings.append("Missing contact phone number.")

        if not profile.education:
            warnings.append("No education records extracted.")

        if not profile.experience:
            warnings.append("No professional experience records extracted.")

        logger.debug("Profile validation completed", warning_count=len(warnings), error_count=len(errors))
        return warnings, errors
