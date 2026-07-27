"""
Pytest integration & unit tests for Phase 9 Enterprise AI Recruitment Decision Agent.
"""

import pytest
from httpx import AsyncClient
from app.matching.schemas.match_models import CandidateMatchReport, ScoreBreakdown
from app.recruitment_agent.pipeline.decision_pipeline import RecruitmentDecisionPipeline
from app.recruitment_agent.schemas.decision_models import DecisionRequest


@pytest.fixture
def decision_pipeline():
    return RecruitmentDecisionPipeline()


@pytest.fixture
def mock_match_report():
    breakdown = ScoreBreakdown(
        qualification_score=1.0,
        experience_score=0.90,
        research_score=0.85,
        teaching_score=0.90,
        skills_score=1.0,
        overall_score=0.92,
    )
    return CandidateMatchReport(
        document_uuid="dec_doc_001",
        job_uuid="dec_job_001",
        candidate_name="Dr. Ananya Roy",
        position_title="Assistant Professor",
        overall_score=0.92,
        score_breakdown=breakdown,
        strengths=["Meets highest academic qualification requirements (Ph.D. degree present)."],
    )


@pytest.mark.anyio
async def test_recruitment_decision_pipeline(
    decision_pipeline: RecruitmentDecisionPipeline, mock_match_report: CandidateMatchReport
):
    request = DecisionRequest(match_report=mock_match_report, department_name="Computer Science & Engineering")
    report = await decision_pipeline.evaluate_candidate_decision(request)

    assert report.candidate_name == "Dr. Ananya Roy"
    assert report.recommendation in ["Highly Recommended", "Recommended"]
    assert report.overall_confidence > 0.50
    assert len(report.specialist_opinions) == 4
    assert len(report.interview_focus) > 0
    assert len(report.evidence) > 0
    assert report.processing_time_ms > 0


@pytest.mark.anyio
async def test_recruitment_decision_api_endpoint(
    async_client: AsyncClient, mock_match_report: CandidateMatchReport
):
    request = DecisionRequest(match_report=mock_match_report)
    payload = request.model_dump(mode="json")

    response = await async_client.post("/api/v1/recruitment/decision", json=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["candidate_name"] == "Dr. Ananya Roy"
    assert "recommendation" in json_data["data"]
    assert "specialist_opinions" in json_data["data"]
