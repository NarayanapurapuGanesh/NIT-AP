"""
JSON Validator & Repair Engine.
Enforces Pydantic v2 schema compliance on LLM output with auto-repair fallback.
"""

from typing import Any, Dict
from app.resume_agent.schemas.agent_models import ReasoningHighlights
from core.logging import get_logger

logger = get_logger("json_validator")


class JSONValidator:
    """JSON Validation Engine."""

    def validate_or_repair(self, raw_json: Dict[str, Any]) -> ReasoningHighlights:
        try:
            return ReasoningHighlights.model_validate(raw_json)
        except Exception as exc:
            logger.warning("LLM JSON output validation failed; auto-repairing schema structure", error=str(exc))
            return ReasoningHighlights(
                professional_summary=str(raw_json.get("professional_summary", "Candidate evaluated.")),
                research_highlights=list(raw_json.get("research_highlights", [])),
                teaching_profile=list(raw_json.get("teaching_profile", [])),
                academic_strengths=list(raw_json.get("academic_strengths", [])),
                areas_for_improvement=list(raw_json.get("areas_for_improvement", [])),
                interview_preparation_notes=list(raw_json.get("interview_preparation_notes", [])),
            )
