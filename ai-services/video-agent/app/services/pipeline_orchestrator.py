"""
FacultyIQ Video Evidence Extraction Service — Pipeline Orchestrator (Modules 11-12).

Master async orchestrator that coordinates all pipeline modules with
config-driven execution, parallel processing, and per-module status tracking.
"""

import asyncio
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Union

from app.config.settings import settings
from app.core.exceptions import PipelineError, ValidationError
from app.core.logging import get_module_logger
from app.models.dtos import FullReportDTO
from app.models.job import (
    JobOutputPaths, JobResponse, JobStatus, ModuleStatus, ProcessingStep,
)
from app.models.ocr import OCRResult
from app.models.scene import SceneDetectionResult
from app.models.summary import TeachingSummary
from app.models.timeline import Timeline
from app.models.transcription import TranscriptionResult
from app.models.validation import VideoMetadata
from app.models.voice import VoiceAnalysisResult
from app.ocr.ocr_service import OCRService
from app.preprocessing.video_preprocessor import PreprocessingResult, VideoPreprocessor
from app.scene_detection.scene_detector import SceneDetector
from app.services.storage_service import StorageService
from app.services.summary_generator import SummaryGenerator
from app.services.timeline_builder import TimelineBuilder
from app.transcription.whisper_transcriber import WhisperTranscriber
from app.validators.video_validator import VideoValidator
from app.voice_analysis.voice_analyzer import VoiceAnalyzer

log = get_module_logger("pipeline")


class PipelineOrchestrator:
    """Orchestrates the complete video evidence extraction pipeline."""

    def __init__(
        self,
        validator: Optional[VideoValidator] = None,
        preprocessor: Optional[VideoPreprocessor] = None,
        transcriber: Optional[WhisperTranscriber] = None,
        scene_detector: Optional[SceneDetector] = None,
        ocr_service: Optional[OCRService] = None,
        timeline_builder: Optional[TimelineBuilder] = None,
        summary_generator: Optional[SummaryGenerator] = None,
        voice_analyzer: Optional[VoiceAnalyzer] = None,
        storage_service: Optional[StorageService] = None,
    ) -> None:
        self._validator = validator or VideoValidator()
        self._preprocessor = preprocessor or VideoPreprocessor()
        self._transcriber = transcriber or WhisperTranscriber()
        self._scene_detector = scene_detector or SceneDetector()
        self._ocr_service = ocr_service or OCRService()
        self._timeline_builder = timeline_builder or TimelineBuilder()
        self._summary_generator = summary_generator or SummaryGenerator()
        self._voice_analyzer = voice_analyzer or VoiceAnalyzer()
        self._storage = storage_service or StorageService()

        self._executor = ThreadPoolExecutor(
            max_workers=settings.pipeline.max_workers
        )
        self._job_store: Dict[str, JobResponse] = {}
        self._report_store: Dict[str, FullReportDTO] = {}

    def get_job_status(self, job_id: str) -> Optional[JobResponse]:
        """Returns the current status of a processing job."""
        return self._job_store.get(job_id)

    def get_report(self, job_id: str) -> Optional[FullReportDTO]:
        """Returns the full report for a completed job."""
        return self._report_store.get(job_id)

    async def process_video(
        self,
        video_path: Union[str, Path],
        job_id: Optional[str] = None,
    ) -> JobResponse:
        """Executes the complete video evidence extraction pipeline."""
        j_id = job_id or str(uuid.uuid4())
        v_path = Path(video_path).resolve()

        pipeline_cfg = settings.pipeline
        steps = self._init_steps(pipeline_cfg)

        job = JobResponse(
            job_id=j_id,
            status=JobStatus.PROCESSING,
            message="Pipeline execution started.",
            video_filename=v_path.name,
            steps=steps,
        )
        self._job_store[j_id] = job

        log.info("[{}] Starting pipeline for: {}", j_id, v_path.name)

        try:
            workspace = self._storage.get_workspace(j_id)

            metadata = await self._run_validation(job, v_path)

            prep_result = await self._run_preprocessing(job, v_path, j_id, metadata)

            loop = asyncio.get_event_loop()

            transcription: Optional[TranscriptionResult] = None
            scene_result: Optional[SceneDetectionResult] = None

            parallel_tasks = []

            if pipeline_cfg.transcription:
                parallel_tasks.append(
                    self._run_in_executor(
                        loop,
                        self._transcribe,
                        job, prep_result.audio_path, workspace,
                    )
                )

            if pipeline_cfg.frame_extraction:
                parallel_tasks.append(
                    self._run_in_executor(
                        loop,
                        self._detect_scenes,
                        job, prep_result.normalized_video_path, workspace,
                    )
                )

            if parallel_tasks:
                results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, Exception):
                        log.error("[{}] Parallel task failed: {}", j_id, result)
                    elif isinstance(result, TranscriptionResult):
                        transcription = result
                    elif isinstance(result, SceneDetectionResult):
                        scene_result = result

            ocr_result: Optional[OCRResult] = None
            if pipeline_cfg.ocr and scene_result:
                ocr_result = await self._run_in_executor(
                    loop, self._run_ocr, job, scene_result, workspace
                )

            voice_result: Optional[VoiceAnalysisResult] = None
            if pipeline_cfg.voice_analysis:
                word_count = len(transcription.full_text.split()) if transcription else 0
                voice_result = await self._run_in_executor(
                    loop,
                    self._run_voice_analysis,
                    job, prep_result.audio_path, workspace, word_count,
                )

            timeline: Optional[Timeline] = None
            if pipeline_cfg.timeline:
                duration = metadata.duration_seconds if metadata else 0.0
                timeline = await self._run_in_executor(
                    loop,
                    self._build_timeline,
                    job, transcription, scene_result, ocr_result,
                    str(workspace / "timeline.json"), duration,
                )

            summary: Optional[TeachingSummary] = None
            if pipeline_cfg.summary:
                summary = await self._run_in_executor(
                    loop,
                    self._generate_summary,
                    job, transcription, ocr_result,
                    str(workspace / "summary.json"),
                )

            gallery_path = str(workspace / "gallery.json")
            self._storage.build_gallery(scene_result, ocr_result, gallery_path)

            report_path = str(workspace / "report.json")
            report = self._storage.build_full_report(
                job_id=j_id,
                metadata=metadata,
                transcription=transcription,
                scene_detection=scene_result,
                ocr=ocr_result,
                timeline=timeline,
                summary=summary,
                voice=voice_result,
                output_path=report_path,
            )
            self._report_store[j_id] = report

            output_paths = JobOutputPaths(
                metadata_json=str(prep_result.metadata_path),
                transcript_json=transcription.json_path if transcription else None,
                transcript_txt=transcription.txt_path if transcription else None,
                slides_dir=scene_result.slides_dir if scene_result else None,
                ocr_json=ocr_result.json_path if ocr_result else None,
                ocr_txt=ocr_result.txt_path if ocr_result else None,
                timeline_json=timeline.json_path if timeline else None,
                summary_json=summary.json_path if summary else None,
                gallery_json=gallery_path,
                voice_json=voice_result.json_path if voice_result else None,
                report_json=report_path,
            )

            job.status = JobStatus.COMPLETED
            job.message = "Pipeline completed successfully."
            job.completed_at = datetime.now(timezone.utc).isoformat()
            job.output = output_paths

            log.info("[{}] Pipeline completed successfully.", j_id)
            return job

        except ValidationError as exc:
            job.status = JobStatus.FAILED
            job.message = f"Validation failed: {exc.message}"
            job.errors = [exc.message]
            log.error("[{}] Pipeline failed at validation: {}", j_id, exc.message)
            return job

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.message = f"Pipeline failed: {str(exc)}"
            job.errors = [str(exc)]
            log.error("[{}] Pipeline failed: {}", j_id, exc)
            return job

    def _init_steps(self, cfg) -> list[ProcessingStep]:
        """Creates processing step entries based on config."""
        step_names = ["validation", "preprocessing"]
        if cfg.transcription:
            step_names.append("transcription")
        if cfg.frame_extraction:
            step_names.append("frame_extraction")
        if cfg.ocr:
            step_names.append("ocr")
        if cfg.voice_analysis:
            step_names.append("voice_analysis")
        if cfg.timeline:
            step_names.append("timeline")
        if cfg.summary:
            step_names.append("summary")
        return [ProcessingStep(module_name=name) for name in step_names]

    def _update_step(
        self, job: JobResponse, module: str, status: ModuleStatus,
        started_at: Optional[float] = None, error: Optional[str] = None,
    ) -> None:
        """Updates a processing step's status."""
        for step in job.steps:
            if step.module_name == module:
                step.status = status
                if status == ModuleStatus.RUNNING:
                    step.started_at = datetime.now(timezone.utc).isoformat()
                elif status in (ModuleStatus.COMPLETED, ModuleStatus.FAILED):
                    step.completed_at = datetime.now(timezone.utc).isoformat()
                    if started_at:
                        step.duration_seconds = round(time.time() - started_at, 2)
                if error:
                    step.error = error
                break

    async def _run_in_executor(self, loop, func, *args):
        """Runs a blocking function in the thread pool executor."""
        return await loop.run_in_executor(self._executor, func, *args)

    async def _run_validation(
        self, job: JobResponse, video_path: Path
    ) -> VideoMetadata:
        """Runs Module 1: Video Validation."""
        start = time.time()
        self._update_step(job, "validation", ModuleStatus.RUNNING)

        result = self._validator.validate(video_path)

        if not result.validation_passed or not result.metadata:
            self._update_step(
                job, "validation", ModuleStatus.FAILED,
                started_at=start, error="; ".join(result.errors),
            )
            raise ValidationError(
                f"Video validation failed: {'; '.join(result.errors)}"
            )

        self._update_step(job, "validation", ModuleStatus.COMPLETED, started_at=start)
        job.warnings.extend(result.warnings)
        return result.metadata

    async def _run_preprocessing(
        self, job: JobResponse, video_path: Path,
        job_id: str, metadata: VideoMetadata,
    ) -> PreprocessingResult:
        """Runs Module 2: Video Preprocessing."""
        start = time.time()
        self._update_step(job, "preprocessing", ModuleStatus.RUNNING)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self._executor,
            self._preprocessor.process,
            video_path, job_id, metadata,
        )

        self._update_step(job, "preprocessing", ModuleStatus.COMPLETED, started_at=start)
        return result

    def _transcribe(
        self, job: JobResponse, audio_path: Path, workspace: Path,
    ) -> TranscriptionResult:
        """Runs Module 3: Speech Transcription."""
        start = time.time()
        self._update_step(job, "transcription", ModuleStatus.RUNNING)

        try:
            result = self._transcriber.transcribe(audio_path, workspace)
            self._update_step(job, "transcription", ModuleStatus.COMPLETED, started_at=start)
            return result
        except Exception as exc:
            self._update_step(
                job, "transcription", ModuleStatus.FAILED,
                started_at=start, error=str(exc),
            )
            raise

    def _detect_scenes(
        self, job: JobResponse, video_path: Path, workspace: Path,
    ) -> SceneDetectionResult:
        """Runs Module 4: Smart Frame Extraction."""
        start = time.time()
        self._update_step(job, "frame_extraction", ModuleStatus.RUNNING)

        try:
            result = self._scene_detector.detect_scenes(video_path, workspace)
            self._update_step(
                job, "frame_extraction", ModuleStatus.COMPLETED, started_at=start
            )
            return result
        except Exception as exc:
            self._update_step(
                job, "frame_extraction", ModuleStatus.FAILED,
                started_at=start, error=str(exc),
            )
            raise

    def _run_ocr(
        self, job: JobResponse, scene_result: SceneDetectionResult, workspace: Path,
    ) -> OCRResult:
        """Runs Module 5: OCR Extraction."""
        start = time.time()
        self._update_step(job, "ocr", ModuleStatus.RUNNING)

        all_slides = [
            slide
            for scene in scene_result.scenes
            for slide in scene.slides
            if not slide.is_duplicate
        ]

        try:
            result = self._ocr_service.process_slides(all_slides, workspace)
            self._update_step(job, "ocr", ModuleStatus.COMPLETED, started_at=start)
            return result
        except Exception as exc:
            self._update_step(
                job, "ocr", ModuleStatus.FAILED,
                started_at=start, error=str(exc),
            )
            raise

    def _run_voice_analysis(
        self, job: JobResponse, audio_path: Path,
        workspace: Path, word_count: int,
    ) -> VoiceAnalysisResult:
        """Runs Module 10: Voice Analysis."""
        start = time.time()
        self._update_step(job, "voice_analysis", ModuleStatus.RUNNING)

        try:
            result = self._voice_analyzer.analyze(audio_path, workspace, word_count)
            self._update_step(
                job, "voice_analysis", ModuleStatus.COMPLETED, started_at=start
            )
            return result
        except Exception as exc:
            self._update_step(
                job, "voice_analysis", ModuleStatus.FAILED,
                started_at=start, error=str(exc),
            )
            raise

    def _build_timeline(
        self, job: JobResponse,
        transcription: Optional[TranscriptionResult],
        scene_result: Optional[SceneDetectionResult],
        ocr_result: Optional[OCRResult],
        output_path: str, duration: float,
    ) -> Timeline:
        """Runs Module 6: Timeline Builder."""
        start = time.time()
        self._update_step(job, "timeline", ModuleStatus.RUNNING)

        try:
            result = self._timeline_builder.build(
                transcription, scene_result, ocr_result,
                output_path, duration,
            )
            self._update_step(job, "timeline", ModuleStatus.COMPLETED, started_at=start)
            return result
        except Exception as exc:
            self._update_step(
                job, "timeline", ModuleStatus.FAILED,
                started_at=start, error=str(exc),
            )
            raise

    def _generate_summary(
        self, job: JobResponse,
        transcription: Optional[TranscriptionResult],
        ocr_result: Optional[OCRResult],
        output_path: str,
    ) -> TeachingSummary:
        """Runs Module 9: Summary Generator."""
        start = time.time()
        self._update_step(job, "summary", ModuleStatus.RUNNING)

        try:
            result = self._summary_generator.generate(
                transcription, ocr_result, output_path
            )
            self._update_step(job, "summary", ModuleStatus.COMPLETED, started_at=start)
            return result
        except Exception as exc:
            self._update_step(
                job, "summary", ModuleStatus.FAILED,
                started_at=start, error=str(exc),
            )
            raise
