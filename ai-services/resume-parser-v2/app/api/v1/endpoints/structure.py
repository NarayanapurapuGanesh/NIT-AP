"""
Resume Structure Endpoint.
POST /api/v1/resume/structure
Receives NormalizedDocument (NDO) payload and extracts semantic resume structure and graph.
"""

from fastapi import APIRouter
from app.document.schemas.normalized_document import NormalizedDocument
from app.resume_structure.pipeline.structure_pipeline import ResumeStructurePipeline
from app.resume_structure.schemas.semantic_resume import SemanticResumeModel
from schemas.base import BaseResponse

router = APIRouter()

structure_pipeline = ResumeStructurePipeline()


@router.post(
    "/resume/structure",
    response_model=BaseResponse[SemanticResumeModel],
    summary="Extract Semantic Resume Structure & Graph",
    description="Processes Normalized Document Object (NDO) to extract sections, hierarchy tree, graph DAG, and evidence.",
)
async def extract_resume_structure(
    normalized_doc: NormalizedDocument,
) -> BaseResponse[SemanticResumeModel]:
    semantic_model = await structure_pipeline.process_structure(normalized_doc)

    return BaseResponse(
        success=True,
        message=f"Resume structure for '{normalized_doc.filename}' extracted successfully ({len(semantic_model.sections)} sections).",
        data=semantic_model,
    )
