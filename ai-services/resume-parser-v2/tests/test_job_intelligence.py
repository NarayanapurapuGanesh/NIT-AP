"""
Pytest integration & unit tests for Phase 7 Enterprise Job Description Intelligence Engine.
"""

import pytest
from httpx import AsyncClient
from app.job_intelligence.pipeline.job_pipeline import JobIntelligencePipeline
from app.job_intelligence.schemas.job_models import JobAnalysisRequest


@pytest.fixture
def job_pipeline():
    return JobIntelligencePipeline()


@pytest.fixture
def mock_job_request():
    jd_text = """
NIT Andhra Pradesh
Recruitment Notification for Assistant Professor (Grade I)
Department: Computer Science & Engineering
Essential Qualifications:
- Ph.D. in Computer Science & Engineering or Artificial Intelligence.
- Minimum 3 years post-Ph.D. teaching/research experience.
- Mandatory Skills: Python, Machine Learning, Data Structures.
- Minimum 3 publications in Scopus / SCI indexed journals.
Responsibilities:
- Deliver undergraduate and postgraduate lectures.
- Conduct independent research and publish in indexed journals.
"""
    return JobAnalysisRequest(
        job_description_text=jd_text,
        job_title="Assistant Professor in Computer Science",
    )


@pytest.mark.anyio
async def test_job_intelligence_pipeline(
    job_pipeline: JobIntelligencePipeline, mock_job_request: JobAnalysisRequest
):
    model = await job_pipeline.process_job_description(mock_job_request)

    assert model.position.academic_rank == "Assistant Professor"
    assert model.qualification.minimum_degree == "Ph.D."
    assert model.qualification.is_phd_mandatory is True
    assert model.experience.min_total_experience_years == 3.0
    assert "Python" in model.skills.mandatory_skills
    assert model.research.scopus_sci_mandatory is True
    assert model.weights.education_weight > 0
    assert model.processing_time_ms > 0


@pytest.mark.anyio
async def test_job_api_endpoint(async_client: AsyncClient, mock_job_request: JobAnalysisRequest):
    payload = mock_job_request.model_dump(mode="json")
    response = await async_client.post("/api/v1/job/analyze", json=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["position"]["academic_rank"] == "Assistant Professor"
    assert json_data["data"]["qualification"]["minimum_degree"] == "Ph.D."
    assert "weights" in json_data["data"]
