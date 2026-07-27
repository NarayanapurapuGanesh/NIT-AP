"""
Resume Agent Endpoint.
POST /api/v1/resume/agent/analyze
Receives AgentAnalysisRequest payload and returns AIResumeIntelligenceReport.
"""

from fastapi import APIRouter
from app.resume_agent.pipeline.agent_pipeline import ResumeAgentPipeline
from app.resume_agent.schemas.agent_models import AIResumeIntelligenceReport, AgentAnalysisRequest
from schemas.base import BaseResponse

router = APIRouter()

agent_pipeline = ResumeAgentPipeline()


@router.post(
    "/resume/agent/analyze",
    response_model=BaseResponse[AIResumeIntelligenceReport],
    summary="Analyze Resume via Local AI Agent",
    description="Executes Local LLM Agent reasoning over Candidate Intelligence Report using Ollama, RAG context, and evidence guardrails.",
)
async def analyze_resume_agent(
    request: AgentAnalysisRequest,
) -> BaseResponse[AIResumeIntelligenceReport]:
    ai_report = await agent_pipeline.analyze_candidate(request)

    return BaseResponse(
        success=True,
        message=f"Local AI Agent reasoning for candidate '{ai_report.candidate_name}' completed using model '{ai_report.token_metrics.model_name}'.",
        data=ai_report,
    )
