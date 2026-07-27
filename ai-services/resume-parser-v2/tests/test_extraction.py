"""
Pytest integration & unit tests for Phase 4 Enterprise Information Extraction Engine.
"""

import pytest
from httpx import AsyncClient
from app.document.schemas.normalized_document import BlockNode, CoordinateBox, EvidencePoint
from app.information_extraction.pipeline.extraction_pipeline import InformationExtractionPipeline
from app.resume_structure.schemas.semantic_resume import SectionNode, SemanticResumeModel


@pytest.fixture
def extraction_pipeline():
    return InformationExtractionPipeline()


@pytest.fixture
def mock_semantic_model():
    box = CoordinateBox(page_number=1, x0=50.0, y0=50.0, x1=550.0, y1=70.0, width=500.0, height=20.0)
    evidence = [EvidencePoint(page_number=1, line_number=1, bounding_box=box, source_engine="pymupdf")]

    header_sec = SectionNode(
        canonical_type="Header",
        original_heading="Header",
        raw_text="Dr. Rajesh Kumar\nProfessor & Head of Department\nemail: r.kumar@nitap.ac.in\nphone: +91-9876543210\nlinkedin.com/in/rajeshkumar\nORCID: 0000-0002-1825-0097",
        evidence=evidence,
    )

    edu_sec = SectionNode(
        canonical_type="Education",
        original_heading="EDUCATION",
        raw_text="Ph.D. in Computer Science\nIndian Institute of Technology Delhi (2014 - 2019)\nCGPA: 9.4/10",
        evidence=evidence,
    )

    exp_sec = SectionNode(
        canonical_type="Professional Experience",
        original_heading="EXPERIENCE",
        raw_text="Professor\nNIT Andhra Pradesh\nJan 2020 - Present\nResponsible for multi-agent research.",
        evidence=evidence,
    )

    skill_sec = SectionNode(
        canonical_type="Skills",
        original_heading="SKILLS",
        raw_text="Programming: Python, Java, C++\nFrameworks: FastAPI, PyTorch, React\nDatabases: PostgreSQL, Qdrant",
        evidence=evidence,
    )

    pub_sec = SectionNode(
        canonical_type="Publications",
        original_heading="PUBLICATIONS",
        raw_text="Kumar, R. (2025). Multi-Agent Systems in Recruitment. IEEE Transactions. doi: 10.1016/j.artint.2025.10398",
        evidence=evidence,
    )

    return SemanticResumeModel(
        document_uuid="test_doc_extract_999",
        filename="dr_rajesh_cv.pdf",
        header_block=header_sec,
        sections=[header_sec, edu_sec, exp_sec, skill_sec, pub_sec],
    )


@pytest.mark.anyio
async def test_information_extraction_pipeline(
    extraction_pipeline: InformationExtractionPipeline, mock_semantic_model: SemanticResumeModel
):
    profile = await extraction_pipeline.extract_candidate_profile(mock_semantic_model)

    assert profile.filename == "dr_rajesh_cv.pdf"

    # Contact tests
    assert profile.contact.full_name.value == "Rajesh Kumar"
    assert profile.contact.email.value == "r.kumar@nitap.ac.in"
    assert profile.contact.orcid.value == "0000-0002-1825-0097"
    assert "linkedin.com/in/rajeshkumar" in profile.contact.linkedin_url.value

    # Education tests
    assert len(profile.education) == 1
    assert profile.education[0].degree.value == "Ph.D."
    assert profile.education[0].cgpa.value == 9.4

    # Experience tests
    assert len(profile.experience) == 1
    assert profile.experience[0].designation.value == "Professor"
    assert profile.experience[0].organization.value == "NIT Andhra Pradesh"
    assert profile.experience[0].is_current is True

    # Skill tests
    assert len(profile.skills) >= 3
    skill_names = [sk.value for cat in profile.skills for sk in cat.skills]
    assert "Python" in skill_names
    assert "PyTorch" in skill_names
    assert "PostgreSQL" in skill_names

    # Publication tests
    assert len(profile.publications) == 1
    assert profile.publications[0].doi.value == "10.1016/j.artint.2025.10398"

    # Knowledge Graph tests
    assert len(profile.knowledge_graph.nodes) > 0
    assert len(profile.knowledge_graph.edges) > 0
    assert profile.processing_time_ms > 0


@pytest.mark.anyio
async def test_extract_api_endpoint(async_client: AsyncClient, mock_semantic_model: SemanticResumeModel):
    payload = mock_semantic_model.model_dump(mode="json")
    response = await async_client.post("/api/v1/resume/extract", json=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["filename"] == "dr_rajesh_cv.pdf"
    assert json_data["data"]["contact"]["email"]["value"] == "r.kumar@nitap.ac.in"
    assert len(json_data["data"]["education"]) == 1
    assert len(json_data["data"]["knowledge_graph"]["nodes"]) > 0


def test_jahnavi_resume_extraction():
    from extractors.deterministic_extractor import DeterministicExtractor

    raw_text = (
        "JAHNAVI NAGABOYINA\n"
        "COMPUTER SCIENCE STUDENT\n\n"
        "CONTACT\n"
        "Phone: +91 8121749977\n"
        "Email Address:\n"
        "nagaboyinajahnavi999@gmail.c\n"
        "om\n"
        "Address: Chodimella,Eluru\n\n"
        "PROFILE\n"
        "Computer Science undergraduate skilled in Figma with hands-on experience in designing and building projects using modern UI/UX practices.\n\n"
        "EDUCATION\n"
        "Bachelor of Technology (B.Tech) 2023 - Present (Expected 2027)\n"
        "Sasi Institute of Technology and Engineering, Tadepalligudem, Andhra Pradesh\n"
        "Intermediate 2021 - 2023\n"
        "Sri Chaitanya Junior College, Eluru, Andhra Pradesh\n"
        "Percentage: 91%\n"
        "Secondary (SSC) 2021\n"
        "Sri Chaitanya School,Andhra Pradesh\n"
        "Percentage: 99.5% CGPA\n\n"
        "TECH SKILLS\n"
        "• Figma\n"
        "• Nano Banana\n"
        "• HTML (Intermediate)\n"
        "• CSS (Intermediate)\n"
        "• Python(Intermediate)\n"
        "• Figjam\n\n"
        "LANGUAGES\n"
        "• English\n\n"
        "ACHIEVEMENTS & CERTIFICATIONS\n"
        "m selected for Smart Indian Hackthon to the 2 Level - 2025\n"
        "m UI/UX Workshop Certification-PurpleLane\n"
        "m 10+ CodeChef Certificates\n"
        "@ AI Internship - Skill Dzire\n"
    )

    extractor = DeterministicExtractor()
    entities = extractor.extract_entities(raw_text)

    # 1. Email verification
    assert entities.email == "nagaboyinajahnavi999@gmail.com"
    assert entities.phone == "+91 8121749977"
    assert entities.name == "Jahnavi Nagaboyina"

    # 2. Education verification
    degrees = [e.degree for e in entities.education]
    assert "Bachelor of Technology (B.Tech)" in degrees
    assert "Intermediate" in degrees
    assert "Secondary (SSC)" in degrees

    # 3. Skills verification
    assert "Nano Banana" in entities.skills
    assert "Figma" in entities.skills
    assert "Python" in entities.skills
    # Check no spurious narrative words like 'practices.' or 'Actively' in skills
    assert "practices." not in entities.skills
    assert "Actively" not in entities.skills

    # 4. Awards & Bullet cleaning verification
    assert len(entities.awards) >= 4
    for award in entities.awards:
        assert not award.startswith("m ")
        assert not award.startswith("@ ")

