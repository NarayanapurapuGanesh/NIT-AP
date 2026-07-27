"""
Pytest integration & unit tests for Phase 3 Resume Structure Intelligence Engine.
"""

import pytest
from httpx import AsyncClient
from app.document.schemas.normalized_document import BlockNode, CoordinateBox, NormalizedDocument, PageNode
from app.resume_structure.heading_classifier import HeadingClassifier
from app.resume_structure.heading_detector import DetectedHeadingCandidate
from app.resume_structure.pipeline.structure_pipeline import ResumeStructurePipeline


@pytest.fixture
def structure_pipeline():
    return ResumeStructurePipeline()


@pytest.fixture
def mock_normalized_doc():
    box = CoordinateBox(page_number=1, x0=50.0, y0=50.0, x1=550.0, y1=70.0, width=500.0, height=20.0)

    header_block = BlockNode(
        block_id="blk_001",
        block_type="text",
        reading_order=1,
        text="Dr. Alice Smith\nProfessor of Computer Science\nalice@university.edu",
        coordinates=box,
    )

    edu_heading_block = BlockNode(
        block_id="blk_002",
        block_type="heading",
        reading_order=2,
        text="EDUCATION",
        coordinates=box,
    )

    edu_text_block = BlockNode(
        block_id="blk_003",
        block_type="text",
        reading_order=3,
        text="Ph.D. in Computer Science, Stanford University, 2018",
        coordinates=box,
    )

    exp_heading_block = BlockNode(
        block_id="blk_004",
        block_type="heading",
        reading_order=4,
        text="ACADEMIC EXPERIENCE",
        coordinates=box,
    )

    exp_text_block = BlockNode(
        block_id="blk_005",
        block_type="text",
        reading_order=5,
        text="Associate Professor, NIT AP (2020 - Present)",
        coordinates=box,
    )

    page = PageNode(
        page_number=1,
        width=612.0,
        height=792.0,
        text="Dr. Alice Smith\nEDUCATION\nACADEMIC EXPERIENCE",
        blocks=[header_block, edu_heading_block, edu_text_block, exp_heading_block, exp_text_block],
    )

    return NormalizedDocument(
        document_uuid="test_doc_12345",
        filename="alice_cv.pdf",
        format_type="pdf",
        classification_type="Native PDF",
        pages=[page],
    )


@pytest.mark.anyio
async def test_structure_pipeline_execution(
    structure_pipeline: ResumeStructurePipeline, mock_normalized_doc: NormalizedDocument
):
    semantic_model = await structure_pipeline.process_structure(mock_normalized_doc)

    assert semantic_model.filename == "alice_cv.pdf"
    assert len(semantic_model.sections) >= 2
    sec_types = [s.canonical_type for s in semantic_model.sections]
    assert "Education" in sec_types
    assert "Academic Experience" in sec_types

    assert len(semantic_model.hierarchy_tree.children) >= 2
    assert len(semantic_model.structure_graph.nodes) > 0
    assert semantic_model.validation_report.quality_score >= 0.50
    assert semantic_model.processing_time_ms > 0


def test_misspelled_heading_normalization():
    classifier = HeadingClassifier()
    cand = DetectedHeadingCandidate(
        raw_text="Educaton",
        block_id="b1",
        page_number=1,
        reading_order=1,
        score=0.80,
    )

    classified = classifier.classify_heading(cand)
    assert classified.canonical_type == "Education"
    assert classified.is_misspelled is True


@pytest.mark.anyio
async def test_structure_api_endpoint(async_client: AsyncClient, mock_normalized_doc: NormalizedDocument):
    payload = mock_normalized_doc.model_dump(mode="json")
    response = await async_client.post("/api/v1/resume/structure", json=payload)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["filename"] == "alice_cv.pdf"
    assert len(json_data["data"]["sections"]) >= 2
    assert "hierarchy_tree" in json_data["data"]
    assert "structure_graph" in json_data["data"]
