"""
FacultyIQ Video Evidence Extraction Service — API Endpoints (Module 14).

FastAPI router providing all video evidence extraction endpoints.
"""

import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import (
    APIRouter, BackgroundTasks, Depends, File, Form,
    HTTPException, UploadFile, status,
)
from fastapi.responses import FileResponse
from loguru import logger

from app.api.dependencies import get_orchestrator
from app.config.settings import settings
from app.models.job import JobResponse
from app.models.validation import ValidationResult
from app.services.pipeline_orchestrator import PipelineOrchestrator
from app.utils.file_utils import ensure_directory

router = APIRouter()


@router.post(
    "/video/upload",
    response_model=ValidationResult,
    summary="Upload and validate a teaching demonstration video",
    description=(
        "Uploads a video file, validates format, MIME type, duration, resolution, "
        "audio presence, and codec compatibility. Returns validation result and metadata."
    ),
)
async def upload_video(
    file: UploadFile = File(...),
    orchestrator: PipelineOrchestrator = Depends(get_orchestrator),
) -> ValidationResult:
    """Endpoint for video upload and Module 1 validation."""
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename missing in uploaded file.",
        )

    upload_dir = ensure_directory(
        settings.base_dir / settings.storage.uploads_dir
    )
    file_id = str(uuid.uuid4())[:8]
    dest_path = upload_dir / f"{file_id}_{file.filename}"

    logger.info("Receiving upload: {} -> {}", file.filename, dest_path)

    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {exc}",
        )

    result = orchestrator._validator.validate(dest_path)
    return result


@router.post(
    "/video/process",
    response_model=JobResponse,
    summary="Process complete video evidence extraction pipeline",
    description=(
        "Triggers the full pipeline: validation → preprocessing → transcription → "
        "frame extraction → OCR → timeline → summary. Runs asynchronously."
    ),
)
async def process_video(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    job_id: Optional[str] = Form(None),
    orchestrator: PipelineOrchestrator = Depends(get_orchestrator),
) -> JobResponse:
    """Triggers the complete evidence extraction pipeline."""
    target_path: Optional[Path] = None
    j_id = job_id or str(uuid.uuid4())

    if file and file.filename:
        upload_dir = ensure_directory(
            settings.base_dir / settings.storage.uploads_dir
        )
        target_path = upload_dir / f"{j_id[:8]}_{file.filename}"
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    elif file_path:
        target_path = Path(file_path).resolve()

    if not target_path or not target_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide a valid uploaded file or 'file_path' parameter.",
        )

    import asyncio
    from app.models.job import JobStatus
    
    asyncio.create_task(orchestrator.process_video(video_path=target_path, job_id=j_id))
    
    return JobResponse(
        job_id=j_id,
        status=JobStatus.QUEUED,
        message="Pipeline execution queued.",
        steps=[],
    )


@router.get(
    "/video/status/{jobId}",
    response_model=JobResponse,
    summary="Get processing job status",
    description="Retrieves job status with per-module progress tracking.",
)
async def get_job_status(
    jobId: str,
    orchestrator: PipelineOrchestrator = Depends(get_orchestrator),
) -> JobResponse:
    """Returns current job processing status."""
    job = orchestrator.get_job_status(jobId)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{jobId}' not found.",
        )
    return job


@router.get(
    "/video/report/{jobId}",
    summary="Get complete evidence report",
    description="Returns the consolidated evidence report with all extracted data.",
)
async def get_report(
    jobId: str,
    orchestrator: PipelineOrchestrator = Depends(get_orchestrator),
):
    """Returns the full evidence report for a completed job."""
    report = orchestrator.get_report(jobId)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report for job '{jobId}' not found.",
        )
    return report.model_dump(by_alias=True)


@router.post(
    "/video/transcript",
    summary="Generate transcript for a video",
    description="Processes only the transcription module for a given video.",
)
async def generate_transcript(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    orchestrator: PipelineOrchestrator = Depends(get_orchestrator),
):
    """Generates transcript only."""
    target_path = await _resolve_file(file, file_path)
    j_id = str(uuid.uuid4())

    val_result = orchestrator._validator.validate(target_path)
    if not val_result.validation_passed or not val_result.metadata:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {'; '.join(val_result.errors)}",
        )

    workspace = orchestrator._storage.get_workspace(j_id)
    prep = orchestrator._preprocessor.process(target_path, j_id, val_result.metadata)
    result = orchestrator._transcriber.transcribe(prep.audio_path, workspace)
    return result.model_dump()


@router.post(
    "/video/slides",
    summary="Extract slides from a video",
    description="Runs scene detection and keyframe extraction only.",
)
async def extract_slides(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    orchestrator: PipelineOrchestrator = Depends(get_orchestrator),
):
    """Extracts slide images from video."""
    target_path = await _resolve_file(file, file_path)
    j_id = str(uuid.uuid4())

    val_result = orchestrator._validator.validate(target_path)
    if not val_result.validation_passed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {'; '.join(val_result.errors)}",
        )

    workspace = orchestrator._storage.get_workspace(j_id)
    result = orchestrator._scene_detector.detect_scenes(target_path, workspace)
    return result.model_dump()


@router.post(
    "/video/ocr",
    summary="Extract OCR text from video slides",
    description="Runs scene detection, keyframe extraction, and OCR.",
)
async def extract_ocr(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    orchestrator: PipelineOrchestrator = Depends(get_orchestrator),
):
    """Extracts OCR text from video slides."""
    target_path = await _resolve_file(file, file_path)
    j_id = str(uuid.uuid4())

    val_result = orchestrator._validator.validate(target_path)
    if not val_result.validation_passed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {'; '.join(val_result.errors)}",
        )

    workspace = orchestrator._storage.get_workspace(j_id)
    scenes = orchestrator._scene_detector.detect_scenes(target_path, workspace)
    all_slides = [
        s for scene in scenes.scenes for s in scene.slides if not s.is_duplicate
    ]
    result = orchestrator._ocr_service.process_slides(all_slides, workspace)
    return result.model_dump()


@router.post(
    "/video/timeline",
    summary="Generate teaching timeline",
    description="Runs full pipeline and returns the unified timeline.",
)
async def generate_timeline(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    orchestrator: PipelineOrchestrator = Depends(get_orchestrator),
):
    """Generates unified teaching timeline."""
    target_path = await _resolve_file(file, file_path)
    j_id = str(uuid.uuid4())
    job = await orchestrator.process_video(target_path, j_id)

    if job.output and job.output.timeline_json:
        import json
        timeline_path = Path(job.output.timeline_json)
        if timeline_path.exists():
            with open(timeline_path, "r", encoding="utf-8") as f:
                return json.load(f)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Timeline generation failed.",
    )


@router.post(
    "/video/summary",
    summary="Generate teaching summary",
    description="Runs full pipeline and returns the teaching summary.",
)
async def generate_summary(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    orchestrator: PipelineOrchestrator = Depends(get_orchestrator),
):
    """Generates teaching summary from extracted evidence."""
    target_path = await _resolve_file(file, file_path)
    j_id = str(uuid.uuid4())
    job = await orchestrator.process_video(target_path, j_id)

    if job.output and job.output.summary_json:
        import json
        summary_path = Path(job.output.summary_json)
        if summary_path.exists():
            with open(summary_path, "r", encoding="utf-8") as f:
                return json.load(f)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Summary generation failed.",
    )


@router.get(
    "/video/slides/{jobId}/images/{slideId}",
    summary="Serve a slide image",
    description="Returns the full-resolution image for a specific slide.",
)
async def get_slide_image(
    jobId: str,
    slideId: str,
):
    """Serves a slide image file."""
    slides_dir = (
        settings.base_dir / settings.storage.output_dir / jobId / "slides"
    )
    image_path = slides_dir / f"{slideId}.jpg"

    if not image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Slide image '{slideId}' not found for job '{jobId}'.",
        )

    return FileResponse(
        path=str(image_path),
        media_type="image/jpeg",
        filename=f"{slideId}.jpg",
    )


async def _resolve_file(
    file: Optional[UploadFile], file_path: Optional[str]
) -> Path:
    """Resolves uploaded file or file path to a local Path."""
    if file and file.filename:
        upload_dir = ensure_directory(
            settings.base_dir / settings.storage.uploads_dir
        )
        dest = upload_dir / f"{uuid.uuid4().hex[:8]}_{file.filename}"
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return dest
    elif file_path:
        p = Path(file_path).resolve()
        if p.exists():
            return p

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Must provide a valid uploaded file or 'file_path' parameter.",
    )
