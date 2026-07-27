"""
Document Classification Endpoint.
POST /api/v1/classify
Accepts file upload and runs deterministic 9-layer classification pipeline.
"""

from fastapi import APIRouter, File, UploadFile
from classifiers.pipeline import DocumentClassificationPipeline
from schemas.base import BaseResponse
from schemas.classification import ClassificationResult
from core.exceptions import ValidationException

router = APIRouter()

classification_pipeline = DocumentClassificationPipeline()


@router.post(
    "/classify",
    response_model=BaseResponse[ClassificationResult],
    summary="Classify Document Type",
    description="Determines document category, confidence score, evidence rules, and acceptance status.",
)
async def classify_document(file: UploadFile = File(...)) -> BaseResponse[ClassificationResult]:
    if not file or not file.filename:
        raise ValidationException("No valid file upload provided.")

    content = await file.read()
    result = await classification_pipeline.classify_file(file.filename, content)

    return BaseResponse(
        success=True,
        message=f"Document classified as '{result.document_type}' with {int(result.confidence * 100)}% confidence.",
        data=result,
    )
