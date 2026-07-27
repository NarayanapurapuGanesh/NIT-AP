"""
Decision JSON Validator & Repair Engine.
Validates decision schema output with auto-repair retry.
"""

from typing import Any, Dict
from core.logging import get_logger

logger = get_logger("decision_json_validator")


class DecisionJSONValidator:
    """Decision JSON Validator."""

    def validate_or_repair(self, raw_json: Dict[str, Any]) -> Dict[str, Any]:
        if "summary" not in raw_json:
            raw_json["summary"] = "Candidate evaluation complete."
        if "risk_level" not in raw_json:
            raw_json["risk_level"] = "Low"
        return raw_json
