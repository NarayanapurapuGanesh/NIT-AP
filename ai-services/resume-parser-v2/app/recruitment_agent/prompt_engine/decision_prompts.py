"""
Decision Prompt Engine.
Builds multi-agent prompts for recruitment decisions, risk assessment, and interview focus areas.
"""

from app.matching.schemas.match_models import CandidateMatchReport
from core.logging import get_logger

logger = get_logger("decision_prompts")


class DecisionPromptEngine:
    """Decision Prompt Builder."""

    def build_decision_prompt(self, match: CandidateMatchReport, rag_policies: str) -> str:
        prompt = f"""
You are the FacultyIQ Multi-Agent Recruitment Decision System evaluating candidate '{match.candidate_name}' for '{match.position_title}'.

=== DETERMINISTIC MATCH REPORT ===
- Overall Score: {int(match.overall_score * 100)}%
- Qualification Score: {int(match.score_breakdown.qualification_score * 100)}%
- Experience Score: {int(match.score_breakdown.experience_score * 100)}%
- Research Score: {int(match.score_breakdown.research_score * 100)}%
- Teaching Score: {int(match.score_breakdown.teaching_score * 100)}%
- Strengths: {", ".join(match.strengths)}
- Critical Gaps: {", ".join(match.critical_gaps)}

=== RAG RECRUITMENT POLICIES ===
{rag_policies}

Return clean JSON:
{{
  "recommendation": "Recommended",
  "summary": "Candidate meets core criteria...",
  "risk_level": "Low",
  "interview_topics": ["Core Research Vision", "Teaching Load Handling"]
}}
"""
        return prompt.strip()
