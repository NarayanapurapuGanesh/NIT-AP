"""
Pytest integration & unit tests for Phase 10 Enterprise Explainability, Audit & Evidence Intelligence Engine.
"""

import pytest
from httpx import AsyncClient
from app.explainability.pipeline.explainability_pipeline import ExplainabilityPipeline
from app.explainability.schemas.explainability_models import ExplainabilityRequest
from app.recruitment_agent.schemas.decision_models import RecruitmentDecisionReport


@pytest.fixture
def explainability_pipeline():
    return ExplainabilityPipeline()


@pytest.fixture
def mock_decision_report():
    return RecruitmentDecisionReport(
        decision_id="test_dec_007",
        document_uuid="doc_exp_007",
        job_uuid="job_exp_007",
        candidate_name="Dr. Vikram Sharma",
        position_title="Professor",
        recommendation="Highly Recommended",
        overall_confidence=0.95,
        summary="Candidate meets all qualifications.",
        evidence=["Matching Overall Score: 95%", "Qualification Score: 100%"],
    )


@pytest.mark.anyio
async def test_explainability_pipeline_execution(
    explainability_pipeline: ExplainabilityPipeline, mock_decision_report: RecruitmentDecisionReport
):
    request = ExplainabilityRequest(decision_report=mock_decision_report, initiator_id="admin_user_1")
    report = await explainability_pipeline.generate_explainability_report(request)

    assert report.candidate_name == "Dr. Vikram Sharma"
    assert report.decision_id == "test_dec_007"
    assert len(report.timeline) == 9
    assert report.audit.initiator_id == "admin_user_1"
    assert report.compliance.is_compliant is True
    assert len(report.explanations) > 0
    assert report.processing_time_ms > 0


@pytest.mark.anyio
async def test_explainability_api_endpoints(
    async_client: AsyncClient, mock_decision_report: RecruitmentDecisionReport
):
    request = ExplainabilityRequest(decision_report=mock_decision_report, initiator_id="admin_user_1")
    payload = request.model_dump(mode="json")

    # 1. Generate report
    response = await async_client.post("/api/v1/explainability/report", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["candidate_name"] == "Dr. Vikram Sharma"
    decision_id = json_data["data"]["decision_id"]

    # 2. Query audit endpoint
    audit_res = await async_client.get(f"/api/v1/audit/{decision_id}")
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert audit_data["success"] is True
    assert audit_data["data"]["initiator_id"] == "admin_user_1"

    # 3. Query evidence endpoint
    ev_res = await async_client.get(f"/api/v1/evidence/{decision_id}")
    assert ev_res.status_code == 200
    ev_data = ev_res.json()
    assert ev_data["success"] is True
    assert len(ev_data["data"]["timeline"]) == 9
