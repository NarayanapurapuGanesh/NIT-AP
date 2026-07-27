"""
Pytest integration & unit tests for Phase 11 Enterprise Interview Intelligence & Assessment System.
"""

import pytest
from httpx import AsyncClient
from app.interview.pipeline.interview_pipeline import InterviewPipeline
from app.interview.schemas.interview_models import (
    CandidateResponseInput,
    EvaluationRequest,
    InterviewPlanRequest,
    QuestionGenerationRequest,
)
from app.recruitment_agent.schemas.decision_models import RecruitmentDecisionReport


@pytest.fixture
def interview_pipeline():
    return InterviewPipeline()


@pytest.fixture
def mock_decision_report():
    return RecruitmentDecisionReport(
        decision_id="dec_int_001",
        document_uuid="doc_int_001",
        job_uuid="job_int_001",
        candidate_name="Dr. Vikram Sharma",
        position_title="Professor",
        recommendation="Highly Recommended",
        overall_confidence=0.95,
        summary="Candidate meets all qualifications.",
    )


@pytest.mark.anyio
async def test_interview_pipeline_plan_generation(
    interview_pipeline: InterviewPipeline, mock_decision_report: RecruitmentDecisionReport
):
    request = InterviewPlanRequest(decision_report=mock_decision_report, department_name="Computer Science")
    plan = await interview_pipeline.generate_interview_plan(request)

    assert plan.candidate_name == "Dr. Vikram Sharma"
    assert len(plan.rounds) == 4
    assert len(plan.question_sets) == 3
    assert len(plan.rubrics) == 5
    assert len(plan.panel) == 4
    assert plan.processing_time_ms > 0


@pytest.mark.anyio
async def test_interview_api_endpoints(
    async_client: AsyncClient, mock_decision_report: RecruitmentDecisionReport
):
    # 1. Generate Interview Plan
    plan_req = InterviewPlanRequest(decision_report=mock_decision_report)
    plan_res = await async_client.post("/api/v1/interview/plan", json=plan_req.model_dump(mode="json"))
    assert plan_res.status_code == 200
    plan_data = plan_res.json()
    assert plan_data["success"] is True
    plan_id = plan_data["data"]["plan_id"]

    # 2. Generate Bloom's Taxonomy Questions
    q_req = QuestionGenerationRequest(
        candidate_name="Dr. Vikram Sharma", position_title="Professor", topics=["Algorithms"]
    )
    q_res = await async_client.post("/api/v1/interview/questions", json=q_req.model_dump(mode="json"))
    assert q_res.status_code == 200
    assert q_res.json()["success"] is True
    assert len(q_res.json()["data"]) == 3

    # 3. Evaluate Responses
    eval_req = EvaluationRequest(
        plan_id=plan_id,
        responses=[CandidateResponseInput(question_id="q1", candidate_answer_text="Ans", score=4)],
    )
    eval_res = await async_client.post("/api/v1/interview/evaluate", json=eval_req.model_dump(mode="json"))
    assert eval_res.status_code == 200
    assert eval_res.json()["success"] is True
    assert eval_res.json()["data"]["overall_interview_score"] > 0

    # 4. Get Report by ID
    rep_res = await async_client.get(f"/api/v1/interview/report/{plan_id}")
    assert rep_res.status_code == 200
    assert rep_res.json()["success"] is True
    assert rep_res.json()["data"]["plan_id"] == plan_id
