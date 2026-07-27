"""
Report Generator Engine.
Generates multi-audience reports (Executive Summary, Technical Report, Hiring Committee Report, Evidence Report, Audit Report, Candidate Explanation).
"""

from typing import Any, Dict
from app.recruitment_agent.schemas.decision_models import RecruitmentDecisionReport
from core.logging import get_logger

logger = get_logger("report_generator")


class ReportGeneratorEngine:
    """Multi-Audience Decision Report Generator Engine."""

    def build_decision_summary(self, decision: RecruitmentDecisionReport) -> Dict[str, Any]:
        return {
            "candidate_name": decision.candidate_name,
            "position_title": decision.position_title,
            "recommendation": decision.recommendation,
            "confidence_pct": int(decision.overall_confidence * 100),
            "summary": decision.summary,
            "risk_level": decision.risks.risk_level,
        }
