"""
Document Ingestion Endpoint.
POST /api/v1/ingest
Accepts document upload and converts it into a canonical NormalizedDocument representation.
"""

from fastapi import APIRouter, File, UploadFile
from app.document.pipeline import DocumentIngestionPipeline
from app.document.schemas.normalized_document import NormalizedDocument
from schemas.base import BaseResponse
from core.exceptions import ValidationException

router = APIRouter()

ingestion_pipeline = DocumentIngestionPipeline()


@router.post(
    "/ingest",
    response_model=BaseResponse[NormalizedDocument],
    summary="Ingest & Extract Document Structure",
    description="Validates, classifies, extracts layout/text/coordinates/evidence, and converts file into NormalizedDocument.",
)
async def ingest_document(file: UploadFile = File(...)) -> BaseResponse[NormalizedDocument]:
    if not file or not file.filename:
        raise ValidationException("No valid file payload provided.")

    content = await file.read()
    normalized_doc = await ingestion_pipeline.ingest_document(file.filename, content)

    return BaseResponse(
        success=True,
        message=f"Document '{file.filename}' successfully ingested ({normalized_doc.classification_type}, {len(normalized_doc.pages)} pages).",
        data=normalized_doc,
    )
