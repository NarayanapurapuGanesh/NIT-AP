"""
Pytest integration & unit tests for Phase 5 Enterprise Resume Intelligence & Validation Engine.
"""

import pytest
from httpx import AsyncClient
from app.information_extraction.schemas.candidate_profile import (
    ContactInfo,
    EducationItem,
    ExperienceItem,
    ExtractedField,
    PublicationItem,
    StructuredCandidateProfile,
)
from app.resume_intelligence.pipeline.intelligence_pipeline import ResumeIntelligencePipeline


@pytest.fixture
def intelligence_pipeline():
    return ResumeIntelligencePipeline()


@pytest.fixture
def mock_candidate_profile():
    contact = ContactInfo(
        full_name=ExtractedField(value="Dr. Vikram Sharma"),
        email=ExtractedField(value="v.sharma@nitap.ac.in"),
        phone=ExtractedField(value="+91-9876543210"),
    )

    edu = EducationItem(
        degree=ExtractedField(value="Ph.D."),
        institution=ExtractedField(value="IIT Bombay"),
        cgpa=ExtractedField(value=9.5),
    )

    exp = ExperienceItem(
        designation=ExtractedField(value="Professor"),
        organization=ExtractedField(value="NIT AP"),
        is_current=True,
    )

    pub = PublicationItem(
        title=ExtractedField(value="AI Agent Systems"),
        doi=ExtractedField(value="10.1016/j.artint.2025.10398"),
        year=ExtractedField(value=2025),
    )

    return StructuredCandidateProfile(
        document_uuid="intel_doc_999",
        filename="vikram_cv.pdf",
        contact=contact,
        education=[edu],
        experience=[exp],
        publications=[pub],
    )


@pytest.mark.anyio
async def test_intelligence_pipeline(
    intelligence_pipeline: ResumeIntelligencePipeline, mock_candidate_profile: StructuredCandidateProfile
):
    report = await intelligence_pipeline.generate_intelligence_report(mock_candidate_profile)

    assert report.candidate_name == "Dr. Vikram Sharma"
    assert report.scores.resume_quality_score > 0.50
    assert report.timeline.teaching_experience_years > 0
    assert report.research.publication_count == 1
    assert report.research.doi_count == 1
    assert report.teaching.has_teaching_experience is True
    assert report.metrics_summary["years_experience"] > 0
    assert report.processing_time_ms > 0


@pytest.mark.anyio
async def test_intelligence_api_endpoint(
    async_client: AsyncClient, mock_candidate_profile: StructuredCandidateProfile
):
    payload = mock_candidate_profile.model_dump(mode="json")
    response = await async_client.post("/api/v1/resume/intelligence", json=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["candidate_name"] == "Dr. Vikram Sharma"
    assert "scores" in json_data["data"]
    assert json_data["data"]["scores"]["resume_quality_score"] > 0
