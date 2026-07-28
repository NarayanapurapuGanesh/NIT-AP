import shutil
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from loguru import logger

from app.api.dependencies import (
    get_full_evaluation_service,
    get_pipeline_service,
    get_visual_pipeline_service,
)
from app.config.settings import settings
from app.models.evidence import EvidencePacket
from app.models.job import JobResponse
from app.models.ocr import OCRResult
from app.models.report import EvaluationReport
from app.models.scene import SceneDetectionResult
from app.models.validation import ValidationResult
from app.models.visual_pipeline import VisualAnalysisResult
from app.services.full_evaluation_service import FullEvaluationService
from app.services.video_pipeline_service import VideoPipelineService
from app.services.visual_pipeline_service import VisualPipelineService
from app.utils.file_utils import ensure_directory

router = APIRouter()


@router.post(
    "/video/upload",
    response_model=ValidationResult,
    summary="Upload and validate a teaching demonstration video",
    description="Uploads video file, performs Phase 1 validation (format, size, duration, codecs, audio presence), and returns validation metadata.",
)
async def upload_video(
    file: UploadFile = File(...),
    pipeline_service: VideoPipelineService = Depends(get_pipeline_service),
) -> ValidationResult:
    """Endpoint for uploading a video file and running Phase 1 validation."""
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename missing in uploaded file.",
        )

    upload_dir = ensure_directory(settings.base_dir / settings.storage.temp_dir / "uploads")
    file_id = str(uuid.uuid4())[:8]
    dest_path = upload_dir / f"{file_id}_{file.filename}"

    logger.info(f"Receiving file upload: {file.filename} -> saving to {dest_path}")

    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}",
        )

    validation_res = pipeline_service.validate_video(dest_path)
    return validation_res


@router.post(
    "/video/process",
    response_model=JobResponse,
    summary="Process video evaluation pipeline (Phases 1-3)",
    description="Triggers Video Evaluation pipeline (Validation -> Preprocessing -> Transcription) for an uploaded video file.",
)
async def process_video(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    job_id: Optional[str] = Form(None),
    pipeline_service: VideoPipelineService = Depends(get_pipeline_service),
) -> JobResponse:
    """Endpoint to trigger video pipeline processing (Phases 1-3)."""
    target_path: Optional[Path] = None
    j_id = job_id or str(uuid.uuid4())

    if file and file.filename:
        upload_dir = ensure_directory(settings.base_dir / settings.storage.temp_dir / "uploads")
        target_path = upload_dir / f"{j_id[:8]}_{file.filename}"
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    elif file_path:
        target_path = Path(file_path).resolve()

    if not target_path or not target_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide a valid uploaded file or existing 'file_path' form parameter.",
        )

    job_res = pipeline_service.process_pipeline(video_path=target_path, job_id=j_id)
    return job_res


@router.get(
    "/video/status/{jobId}",
    response_model=JobResponse,
    summary="Get status of video processing job",
    description="Retrieves job status, warnings, errors, and Phase 1-3 pipeline results when completed.",
)
async def get_job_status(
    jobId: str,
    pipeline_service: VideoPipelineService = Depends(get_pipeline_service),
) -> JobResponse:
    """Endpoint to query job processing status."""
    return pipeline_service.get_job_status(jobId)


@router.post(
    "/video/analyze-visual",
    response_model=VisualAnalysisResult,
    summary="Run Phase 4-6 Visual Analysis Pipeline (Scene Detection, OCR, MediaPipe)",
    description="Executes Phase 4 Scene Detection, Phase 5 Tesseract OCR Slide Structure Analysis, and Phase 6 MediaPipe Face/Pose/Gesture Evaluation.",
)
async def analyze_visual(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    job_id: Optional[str] = Form(None),
    visual_service: VisualPipelineService = Depends(get_visual_pipeline_service),
) -> VisualAnalysisResult:
    """Endpoint executing Phases 4, 5, and 6 visual analysis pipeline."""
    target_path: Optional[Path] = None
    j_id = job_id or str(uuid.uuid4())

    if file and file.filename:
        upload_dir = ensure_directory(settings.base_dir / settings.storage.temp_dir / "uploads")
        target_path = upload_dir / f"{j_id[:8]}_{file.filename}"
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    elif file_path:
        target_path = Path(file_path).resolve()

    if not target_path or not target_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide a valid uploaded file or existing 'file_path' form parameter.",
        )

    res = visual_service.analyze_visual_pipeline(video_path=target_path, job_id=j_id)
    return res


@router.get(
    "/video/scenes/{jobId}",
    response_model=SceneDetectionResult,
    summary="Get Phase 4 Scene Detection & Keyframe timeline for job",
    description="Retrieves detected scenes, transitions, and keyframe paths for a specified job ID.",
)
async def get_scenes(
    jobId: str,
    visual_service: VisualPipelineService = Depends(get_visual_pipeline_service),
) -> SceneDetectionResult:
    """Endpoint retrieving Phase 4 Scene detection result."""
    res = visual_service.get_scenes(jobId)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scene detection results for job '{jobId}' not found.",
        )
    return res


@router.get(
    "/video/ocr/{jobId}",
    response_model=OCRResult,
    summary="Get Phase 5 OCR Slide Content & Structural results for job",
    description="Retrieves extracted slide text, confidence scores, and structural components (titles, headings, code, equations).",
)
async def get_ocr(
    jobId: str,
    visual_service: VisualPipelineService = Depends(get_visual_pipeline_service),
) -> OCRResult:
    """Endpoint retrieving Phase 5 OCR result."""
    res = visual_service.get_ocr(jobId)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OCR results for job '{jobId}' not found.",
        )
    return res


@router.post(
    "/video/evaluate",
    response_model=EvaluationReport,
    summary="Run Complete End-to-End Video Evaluation Pipeline (Phases 1-9)",
    description="Executes all 9 phases (Validation, Preprocessing, Whisper, Scene Detection, OCR, MediaPipe, Voice Analysis, Ollama LLM Teaching Intelligence, Evidence Packet, Scoring Engine, and Report Generator).",
)
async def evaluate_video(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    job_id: Optional[str] = Form(None),
    full_service: FullEvaluationService = Depends(get_full_evaluation_service),
) -> EvaluationReport:
    """Master endpoint executing complete end-to-end video evaluation (Phases 1-9)."""
    target_path: Optional[Path] = None
    j_id = job_id or str(uuid.uuid4())

    if file and file.filename:
        upload_dir = ensure_directory(settings.base_dir / settings.storage.temp_dir / "uploads")
        target_path = upload_dir / f"{j_id[:8]}_{file.filename}"
        logger.info(f"Receiving video for full evaluation: {file.filename} -> saving to {target_path}")
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    elif file_path:
        target_path = Path(file_path).resolve()

    if not target_path or not target_path.exists():
        logger.warning("HTTP 400: Neither file nor file_path provided or target_path does not exist.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide a valid uploaded file or existing 'file_path' form parameter.",
        )

    report = full_service.evaluate_video_full(video_path=target_path, job_id=j_id)
    return report


@router.get(
    "/video/report/{jobId}",
    response_model=EvaluationReport,
    summary="Get Phase 9 Final Evaluation Report for job",
    description="Retrieves the final evaluation report, weighted category scores, strengths, weaknesses, and hiring recommendation.",
)
async def get_report(
    jobId: str,
    full_service: FullEvaluationService = Depends(get_full_evaluation_service),
) -> EvaluationReport:
    """Endpoint retrieving Phase 9 final report."""
    report = full_service.get_report(jobId)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation report for job '{jobId}' not found.",
        )
    return report


@router.get(
    "/video/evidence/{jobId}",
    response_model=EvidencePacket,
    summary="Get Phase 9 Evidence Packet for job",
    description="Retrieves merged Evidence Packet containing video, speech, visual, and teaching evidence metrics.",
)
async def get_evidence(
    jobId: str,
    full_service: FullEvaluationService = Depends(get_full_evaluation_service),
) -> EvidencePacket:
    """Endpoint retrieving Phase 9 evidence packet."""
    evidence = full_service.get_evidence(jobId)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence packet for job '{jobId}' not found.",
        )
    return evidence
