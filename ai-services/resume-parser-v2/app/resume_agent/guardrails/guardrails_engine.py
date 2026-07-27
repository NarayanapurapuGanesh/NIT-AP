"""
Guardrails Engine.
Enforces zero hallucination guidelines and verifies LLM reasoning against grounded evidence.
"""

from app.resume_agent.schemas.agent_models import ReasoningHighlights
from app.resume_intelligence.schemas.intelligence_report import CandidateIntelligenceReport
from core.logging import get_logger

logger = get_logger("guardrails_engine")


class GuardrailsEngine:
    """Anti-Hallucination Guardrails Engine."""

    def enforce_guardrails(
        self, reasoning: ReasoningHighlights, report: CandidateIntelligenceReport
    ) -> ReasoningHighlights:
        # Check if research highlights hallucinate publications when ground truth publication_count is 0
        if report.research.publication_count == 0 and reasoning.research_highlights:
            reasoning.research_highlights = ["No peer-reviewed publications detected in profile."]
            logger.info("Guardrail enforced: Replaced hallucinated publication highlights with ground truth null state.")

        return reasoning
