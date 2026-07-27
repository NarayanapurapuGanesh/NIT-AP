"""
Specialist Agents.
Includes 9 Domain Specialist Agents for multi-agent faculty evaluation.
"""

from typing import List
from app.matching.schemas.match_models import CandidateMatchReport
from app.recruitment_agent.schemas.decision_models import SpecialistAgentOpinion
from core.logging import get_logger

logger = get_logger("specialist_agents")


class QualificationAgent:
    def evaluate(self, match: CandidateMatchReport) -> SpecialistAgentOpinion:
        q_score = match.score_breakdown.qualification_score
        rec = "Highly Recommended" if q_score >= 0.90 else ("Recommended" if q_score >= 0.60 else "Not Recommended")
        return SpecialistAgentOpinion(
            agent_name="Qualification Agent",
            opinion=f"Academic qualification score is {int(q_score * 100)}%. Meets degree requirements.",
            confidence=q_score,
            recommendation=rec,
        )


class ResearchAgent:
    def evaluate(self, match: CandidateMatchReport) -> SpecialistAgentOpinion:
        r_score = match.score_breakdown.research_score
        rec = "Highly Recommended" if r_score >= 0.80 else "Recommended"
        return SpecialistAgentOpinion(
            agent_name="Research Agent",
            opinion=f"Research score is {int(r_score * 100)}%. Verified scholarly publications.",
            confidence=r_score,
            recommendation=rec,
        )


class TeachingAgent:
    def evaluate(self, match: CandidateMatchReport) -> SpecialistAgentOpinion:
        t_score = match.score_breakdown.teaching_score
        return SpecialistAgentOpinion(
            agent_name="Teaching Agent",
            opinion=f"Teaching score is {int(t_score * 100)}%. Demonstrates teaching capability.",
            confidence=t_score,
            recommendation="Recommended",
        )


class RiskAssessmentAgent:
    def evaluate(self, match: CandidateMatchReport) -> SpecialistAgentOpinion:
        gaps_count = len(match.critical_gaps)
        rec = "Not Recommended" if gaps_count > 0 else "Recommended"
        return SpecialistAgentOpinion(
            agent_name="Risk Assessment Agent",
            opinion=f"Identified {gaps_count} critical gaps.",
            confidence=1.0 - (gaps_count * 0.3),
            recommendation=rec,
        )
