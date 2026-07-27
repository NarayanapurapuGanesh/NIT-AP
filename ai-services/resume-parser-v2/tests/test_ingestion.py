"""
Pytest integration & unit tests for Phase 2 Document Ingestion & Extraction Engine.
"""

import pytest
from httpx import AsyncClient
from app.document.exceptions.ingestion_exceptions import DocumentValidationException
from app.document.pipeline import DocumentIngestionPipeline


@pytest.fixture
def ingestion_pipeline():
    return DocumentIngestionPipeline()


@pytest.mark.anyio
async def test_pdf_document_ingestion(ingestion_pipeline: DocumentIngestionPipeline):
    # Minimal valid PDF binary header
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kinds [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj\n"
        b"4 0 obj << /Length 55 >> stream\n"
        b"BT /F1 12 Tf 50 700 Td (Academic CV - Dr. Jane Doe) Tj ET\n"
        b"endstream endobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer << /Size 5 /Root 1 0 R >>\n"
        b"startxref\n300\n%%EOF"
    )

    doc = await ingestion_pipeline.ingest_document("jane_cv.pdf", pdf_content)
    assert doc.format_type == "pdf"
    assert doc.classification_type in ["Native PDF", "Scanned PDF", "Hybrid PDF"]
    assert len(doc.pages) == 1
    assert doc.metadata.file_hash != ""
    assert doc.statistics.char_count >= 0
    assert doc.processing_time_ms > 0


@pytest.mark.anyio
async def test_docx_document_ingestion(ingestion_pipeline: DocumentIngestionPipeline):
    docx_text = b"Faculty Resume\nDr. Alex Rivera\nAssociate Professor of Computer Science"

    doc = await ingestion_pipeline.ingest_document("alex_resume.txt", docx_text)
    assert doc.format_type in ["txt", "docx"]
    assert len(doc.pages) == 1
    assert "Alex Rivera" in doc.pages[0].text
    assert len(doc.reading_order_blocks) > 0


@pytest.mark.anyio
async def test_corrupted_file_validation(ingestion_pipeline: DocumentIngestionPipeline):
    tiny_content = b"a"  # Under min file size threshold
    with pytest.raises(DocumentValidationException):
        await ingestion_pipeline.ingest_document("invalid.pdf", tiny_content)


@pytest.mark.anyio
async def test_ingest_api_endpoint(async_client: AsyncClient):
    cv_content = (
        b"%PDF-1.5\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Count 1 >> endobj\n"
        b"startxref\n100\n%%EOF"
    )

    files = {"file": ("professor_cv.pdf", cv_content, "application/pdf")}
    response = await async_client.post("/api/v1/ingest", files=files)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["filename"] == "professor_cv.pdf"
    assert "document_uuid" in json_data["data"]
    assert "statistics" in json_data["data"]
