"""
Prompt Template Engine.
Builds structured prompts for candidate summary, research highlights, teaching profile, academic strengths, and interview notes.
"""

from typing import Optional
from app.resume_agent.schemas.agent_models import AgentAnalysisRequest
from core.logging import get_logger

logger = get_logger("prompt_engine")


class PromptEngine:
    """Prompt Builder Engine."""

    def build_agent_prompt(self, request: AgentAnalysisRequest, policy_context: str) -> str:
        report = request.intelligence_report
        scores = report.scores
        timeline = report.timeline

        prompt = f"""
You are the FacultyIQ Resume Intelligence Agent evaluating candidate '{report.candidate_name}' for department '{request.department_name}'.

=== DETERMINISTIC FACTS (AUTHENTIC GROUND TRUTH) ===
- Candidate Name: {report.candidate_name}
- Total Experience: {timeline.total_experience_years} years
- Teaching Experience: {timeline.teaching_experience_years} years
- Research Experience: {timeline.research_experience_years} years
- Industry Experience: {timeline.industry_experience_years} years
- Publications Count: {report.research.publication_count} (DOIs: {report.research.doi_count})
- Highest Academic Rank: {report.teaching.highest_academic_rank or "N/A"}
- Overall Resume Quality Score: {scores.resume_quality_score * 100}%
- Recommendations: {", ".join(report.recommendations)}

=== INSTITUTIONAL POLICY RAG CONTEXT ===
{policy_context}

=== TARGET JOB DESCRIPTION ===
{request.job_description or "Standard Assistant/Associate Professor Faculty Position"}

=== MANDATORY INSTRUCTIONS ===
1. Reason ONLY over the ground truth provided above.
2. DO NOT invent or hallucinate dates, degrees, or employers.
3. Return clean JSON strictly following this schema:
{{
  "professional_summary": "Executive candidate overview...",
  "research_highlights": ["Highlight 1", "Highlight 2"],
  "teaching_profile": ["Teaching detail 1"],
  "academic_strengths": ["Strength 1"],
  "areas_for_improvement": ["Improvement point 1"],
  "interview_preparation_notes": ["Interview question 1"]
}}
"""
        logger.debug("Agent prompt built", candidate=report.candidate_name)
        return prompt.strip()
