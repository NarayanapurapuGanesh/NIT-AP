"""
Pytest integration & unit tests for Phase 6 Enterprise Resume Intelligence Agent.
"""

import pytest
from httpx import AsyncClient
from app.resume_agent.pipeline.agent_pipeline import ResumeAgentPipeline
from app.resume_agent.schemas.agent_models import AgentAnalysisRequest
from app.resume_intelligence.schemas.intelligence_report import CandidateIntelligenceReport, ProfileQualityScores, ResearchIntelligence, TeachingIntelligence, TimelineAnalysis


@pytest.fixture
def agent_pipeline():
    return ResumeAgentPipeline()


@pytest.fixture
def mock_agent_request():
    report = CandidateIntelligenceReport(
        document_uuid="agent_doc_100",
        filename="dr_ananya_cv.pdf",
        candidate_name="Dr. Ananya Roy",
        scores=ProfileQualityScores(resume_quality_score=0.92, research_strength_score=0.85),
        timeline=TimelineAnalysis(total_experience_years=6.0, teaching_experience_years=4.0, research_experience_years=2.0),
        research=ResearchIntelligence(publication_count=5, doi_count=4),
        teaching=TeachingIntelligence(has_teaching_experience=True, highest_academic_rank="Associate Professor"),
    )

    return AgentAnalysisRequest(
        intelligence_report=report,
        department_name="Computer Science & Engineering",
        preferred_model="llama3.2",
    )


@pytest.mark.anyio
async def test_agent_pipeline_execution(
    agent_pipeline: ResumeAgentPipeline, mock_agent_request: AgentAnalysisRequest
):
    ai_report = await agent_pipeline.analyze_candidate(mock_agent_request)

    assert ai_report.candidate_name == "Dr. Ananya Roy"
    assert ai_report.overall_agent_confidence >= 0.50
    assert len(ai_report.reasoning.professional_summary) > 10
    assert len(ai_report.citations) > 0
    assert ai_report.token_metrics.total_tokens > 0
    assert ai_report.processing_time_ms > 0


@pytest.mark.anyio
async def test_agent_api_endpoint(async_client: AsyncClient, mock_agent_request: AgentAnalysisRequest):
    payload = mock_agent_request.model_dump(mode="json")
    response = await async_client.post("/api/v1/resume/agent/analyze", json=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["candidate_name"] == "Dr. Ananya Roy"
    assert "reasoning" in json_data["data"]
    assert "citations" in json_data["data"]
    assert json_data["data"]["overall_agent_confidence"] > 0
