"""
Enterprise Quality & Production Certification REST API Endpoints.
GET /api/v1/platform/readiness
GET /api/v1/platform/benchmark
GET /api/v1/platform/certification
"""

from typing import Any, Dict
from fastapi import APIRouter
from quality.pipeline.quality_pipeline import QualityPipeline
from quality.schemas.quality_models import ProductionReadinessReport
from schemas.base import BaseResponse

router = APIRouter()

quality_pipeline = QualityPipeline()


@router.get(
    "/platform/readiness",
    response_model=BaseResponse[Dict[str, Any]],
    summary="Get Production Readiness Status",
    description="Returns live production readiness score, checklist items passed, and overall readiness boolean.",
)
async def get_readiness() -> BaseResponse[Dict[str, Any]]:
    status_data = quality_pipeline.get_readiness_status()
    return BaseResponse(success=True, message=f"Readiness score: {status_data['score_percent']}%", data=status_data)


@router.get(
    "/platform/benchmark",
    response_model=BaseResponse[Dict[str, Any]],
    summary="Run Benchmark Suite",
    description="Runs full performance benchmark and AI Agent evaluation suite.",
)
async def run_benchmark() -> BaseResponse[Dict[str, Any]]:
    benchmark_data = quality_pipeline.run_benchmark_suite()
    return BaseResponse(success=True, message="Benchmark suite completed successfully.", data=benchmark_data)


@router.get(
    "/platform/certification",
    response_model=BaseResponse[ProductionReadinessReport],
    summary="Get Production Certification Report",
    description="Returns formal 9-part Production Readiness Certification Report.",
)
async def get_certification() -> BaseResponse[ProductionReadinessReport]:
    report = quality_pipeline.generate_full_certification_report()
    return BaseResponse(success=True, message="Master Production Readiness Certification Report generated.", data=report)
