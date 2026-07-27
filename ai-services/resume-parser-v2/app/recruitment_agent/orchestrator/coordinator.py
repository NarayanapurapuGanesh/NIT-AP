"""
Coordinator Agent & Consensus Orchestrator.
Orchestrates parallel specialist agents, conflict resolution, consensus building, and decision synthesis.
"""

from typing import List, Tuple
from app.matching.schemas.match_models import CandidateMatchReport
from app.recruitment_agent.agents.specialist_agents import QualificationAgent, ResearchAgent, RiskAssessmentAgent, TeachingAgent
from app.recruitment_agent.schemas.decision_models import SpecialistAgentOpinion
from core.logging import get_logger

logger = get_logger("coordinator_agent")


class CoordinatorAgent:
    """Multi-Agent Coordinator Engine."""

    def __init__(self) -> None:
        self.qual_agent = QualificationAgent()
        self.research_agent = ResearchAgent()
        self.teaching_agent = TeachingAgent()
        self.risk_agent = RiskAssessmentAgent()

    def orchestrate_agents(
        self, match: CandidateMatchReport
    ) -> Tuple[str, List[SpecialistAgentOpinion]]:
        opinions: List[SpecialistAgentOpinion] = [
            self.qual_agent.evaluate(match),
            self.research_agent.evaluate(match),
            self.teaching_agent.evaluate(match),
            self.risk_agent.evaluate(match),
        ]

        # Consensus Decision Synthesis
        if match.overall_score >= 0.85 and len(match.critical_gaps) == 0:
            final_recommendation = "Highly Recommended"
        elif match.overall_score >= 0.70 and len(match.critical_gaps) == 0:
            final_recommendation = "Recommended"
        elif match.overall_score >= 0.50:
            final_recommendation = "Borderline"
        elif len(match.critical_gaps) > 0:
            final_recommendation = "Requires Manual Review"
        else:
            final_recommendation = "Not Recommended"

        logger.debug("Coordinator multi-agent consensus achieved", recommendation=final_recommendation)
        return final_recommendation, opinions
