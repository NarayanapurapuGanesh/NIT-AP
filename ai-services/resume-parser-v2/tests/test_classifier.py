"""
Pytest unit tests for Document Classification Engine.
"""

import pytest
from httpx import AsyncClient
from classifiers.pipeline import DocumentClassificationPipeline
from core.exceptions import ValidationException


@pytest.fixture
def classifier_pipeline():
    return DocumentClassificationPipeline()


@pytest.mark.anyio
async def test_faculty_cv_classification(classifier_pipeline: DocumentClassificationPipeline):
    cv_content = (
        b"CURRICULUM VITAE\n"
        b"Dr. Rajesh Kumar\n"
        b"Professor & Head of Department\n"
        b"Department of Computer Science & Engineering\n\n"
        b"PUBLICATIONS & JOURNAL ARTICLES\n"
        b"1. Kumar, R. (2024). Multi-agent systems in higher education. IEEE Transactions, 12(3).\n\n"
        b"RESEARCH GRANTS & PATENTS\n"
        b"Principal Investigator, DST Sponsored Research Grant ($150,000)\n"
        b"PhD Supervised: 5 candidates graduated.\n"
    )

    result = await classifier_pipeline.classify_file("dr_kumar_cv.pdf", cv_content)
    assert result.document_type == "Faculty CV"
    assert result.confidence >= 0.50
    assert result.accepted is True
    assert result.next_stage == "TextExtraction"
    assert len(result.evidence) > 0


@pytest.mark.anyio
async def test_invoice_classification(classifier_pipeline: DocumentClassificationPipeline):
    invoice_content = (
        b"TAX INVOICE # INV-2026-0042\n"
        b"BILL TO: NIT Andhra Pradesh\n"
        b"GSTIN: 37AAAAA0000A1Z5\n\n"
        b"DESCRIPTION | QUANTITY | UNIT PRICE | AMOUNT\n"
        b"Server Hardware | 2 | 5000 | 10000\n\n"
        b"SUBTOTAL: $10,000\n"
        b"TOTAL AMOUNT DUE: $10,000\n"
    )

    result = await classifier_pipeline.classify_file("invoice_123.pdf", invoice_content)
    assert result.document_type == "Invoice"
    assert result.accepted is False
    assert result.next_stage == "SpecializedHandler"


@pytest.mark.anyio
async def test_research_paper_classification(classifier_pipeline: DocumentClassificationPipeline):
    paper_content = (
        b"Deep Learning Techniques for Document Intelligence\n\n"
        b"ABSTRACT\n"
        b"This paper presents a novel approach to offline document classification.\n\n"
        b"INTRODUCTION\n"
        b"Document classification plays a critical role in automated enterprise ingestion pipelines.\n\n"
        b"METHODOLOGY & EXPERIMENTAL RESULTS\n"
        b"We evaluate benchmark datasets across multiple categories.\n\n"
        b"REFERENCES\n"
        b"1. Smith et al. (2025). doi:10.1016/j.artint.2025.10398\n"
    )

    result = await classifier_pipeline.classify_file("research_paper.pdf", paper_content)
    assert result.document_type == "Research Paper"
    assert result.accepted is False
    assert result.next_stage == "SpecializedHandler"


@pytest.mark.anyio
async def test_unknown_document_classification(classifier_pipeline: DocumentClassificationPipeline):
    random_content = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor."

    result = await classifier_pipeline.classify_file("random.txt", random_content)
    assert result.document_type == "Unknown"
    assert result.accepted is False
    assert result.next_stage == "Rejected"


@pytest.mark.anyio
async def test_empty_document_validation(classifier_pipeline: DocumentClassificationPipeline):
    with pytest.raises(ValidationException):
        await classifier_pipeline.classify_file("empty.pdf", b"")


@pytest.mark.anyio
async def test_classify_api_endpoint(async_client: AsyncClient):
    cv_content = (
        b"CURRICULUM VITAE\n"
        b"Prof. Anita Sharma\n"
        b"Associate Professor\n"
        b"PUBLICATIONS & PATENTS\n"
        b"IEEE Journal 2025\n"
    )

    files = {"file": ("anita_cv.pdf", cv_content, "application/pdf")}
    response = await async_client.post("/api/v1/classify", files=files)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["document_type"] == "Faculty CV"
    assert json_data["data"]["accepted"] is True
    assert "processing_time_ms" in json_data["data"]
