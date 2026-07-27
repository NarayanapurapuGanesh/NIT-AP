"""
Agent Confidence Engine.
Calculates overall reasoning confidence score combining model, evidence, and retrieval scores.
"""

from app.resume_intelligence.schemas.intelligence_report import CandidateIntelligenceReport
from core.logging import get_logger

logger = get_logger("agent_confidence")


class AgentConfidenceEngine:
    """Agent Confidence Evaluator."""

    def compute_confidence(self, report: CandidateIntelligenceReport) -> float:
        base_confidence = report.scores.evidence_strength_score
        final_score = round(min(1.0, max(0.50, base_confidence)), 2)
        return final_score
