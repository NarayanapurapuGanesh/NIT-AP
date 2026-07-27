"""
Explainability, Audit & Evidence Endpoints.
POST /api/v1/explainability/report
GET /api/v1/audit/{decision_id}
GET /api/v1/evidence/{candidate_id}
"""

from fastapi import APIRouter, HTTPException, Path
from app.explainability.pipeline.explainability_pipeline import ExplainabilityPipeline
from app.explainability.schemas.explainability_models import AuditRecord, ExplainabilityReport, ExplainabilityRequest
from app.explainability.services.audit_service import AuditRepositoryService
from schemas.base import BaseResponse

router = APIRouter()

explainability_pipeline = ExplainabilityPipeline()
audit_service = AuditRepositoryService.get_instance()


@router.post(
    "/explainability/report",
    response_model=BaseResponse[ExplainabilityReport],
    summary="Generate Explainability & Audit Report",
    description="Generates transparent, auditable, and legally defensible explanation report for recruitment decision.",
)
async def generate_explainability_report(
    request: ExplainabilityRequest,
) -> BaseResponse[ExplainabilityReport]:
    report = await explainability_pipeline.generate_explainability_report(request)

    return BaseResponse(
        success=True,
        message=f"Explainability and audit report for candidate '{report.candidate_name}' generated successfully.",
        data=report,
    )


@router.get(
    "/audit/{decision_id}",
    response_model=BaseResponse[AuditRecord],
    summary="Retrieve Audit Log Record by Decision ID",
    description="Fetches immutable audit record containing timestamp, configuration hash, model version, and citation IDs.",
)
async def get_audit_record(
    decision_id: str = Path(..., description="Unique decision ID"),
) -> BaseResponse[AuditRecord]:
    record = audit_service.get_audit_record(decision_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Audit record for decision_id '{decision_id}' not found.")

    return BaseResponse(
        success=True,
        message=f"Audit record for decision_id '{decision_id}' retrieved.",
        data=record,
    )


@router.get(
    "/evidence/{candidate_id}",
    response_model=BaseResponse[ExplainabilityReport],
    summary="Retrieve Candidate Evidence Provenance Report",
    description="Fetches complete evidence citations and pipeline stage timeline for candidate.",
)
async def get_candidate_evidence(
    candidate_id: str = Path(..., description="Decision ID or Candidate ID"),
) -> BaseResponse[ExplainabilityReport]:
    report = audit_service.get_report(candidate_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Evidence report for candidate_id '{candidate_id}' not found.")

    return BaseResponse(
        success=True,
        message=f"Evidence report for candidate_id '{candidate_id}' retrieved.",
        data=report,
    )
