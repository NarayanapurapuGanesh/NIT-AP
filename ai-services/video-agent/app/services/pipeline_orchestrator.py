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
from typing import Dict, Optional, Union, Tuple, List

from app.config.settings import settings
from app.core.exceptions import PipelineError, ValidationError
from app.core.logging import get_module_logger
from app.models.dtos import FullReportDTO, SlideDTO
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
from app.db.session import SessionLocal

from app.visual_extractor.gallery_service import (
    extract_representative_frames,
    run_diagram_ai,
    run_ocr_ai,
    assemble_visual_evidence
)
from app.utils.file_utils import write_json

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

            # --- PARALLEL MICRO-PIPELINES ---
            audio_task = asyncio.create_task(
                self._run_audio_pipeline(loop, job, prep_result.audio_path, workspace)
            )
            frame_task = asyncio.create_task(
                self._run_frame_pipeline(loop, job, prep_result.normalized_video_path, workspace)
            )

            # Wait for all evidence engines
            audio_res, frame_res = await asyncio.gather(audio_task, frame_task, return_exceptions=True)

            transcription, voice_result = audio_res if not isinstance(audio_res, Exception) else (None, None)
            if isinstance(audio_res, Exception):
                log.error(f"[{j_id}] Audio Pipeline failed: {audio_res}")

            frames, diag_res, ocr_res = frame_res if not isinstance(frame_res, Exception) else ([], {}, {})
            if isinstance(frame_res, Exception):
                log.error(f"[{j_id}] Frame Pipeline failed: {frame_res}")

            # --- ASSEMBLE VISUALS ---
            visuals: List[SlideDTO] = []
            if frames:
                try:
                    visuals = await self._run_in_executor(
                        loop, self._assemble_visuals, job, j_id, frames, diag_res, ocr_res, transcription, workspace
                    )
                except Exception as exc:
                    log.error(f"[{j_id}] Visual Assembly failed: {exc}")
            else:
                self._update_step(job, "visual_assembly", ModuleStatus.SKIPPED, error="No frames extracted")

            # --- DOWNSTREAM (Timeline, Summary) ---
            downstream_tasks = []
            if pipeline_cfg.timeline:
                duration = metadata.duration_seconds if metadata else 0.0
                downstream_tasks.append(
                    self._run_in_executor(
                        loop, self._build_timeline, job, transcription, visuals, str(workspace / "timeline.json"), duration
                    )
                )

            if pipeline_cfg.summary:
                visuals_count = len(visuals) if visuals else 0
                downstream_tasks.append(
                    self._run_in_executor(
                        loop, self._generate_summary, job, transcription, visuals, str(workspace / "summary.json"), visuals_count
                    )
                )

            downstream_results = await asyncio.gather(*downstream_tasks, return_exceptions=True)
            
            timeline = None
            summary = None
            
            for res in downstream_results:
                if isinstance(res, Timeline): timeline = res
                elif isinstance(res, TeachingSummary): summary = res
                elif isinstance(res, Exception): log.error(f"[{j_id}] Downstream task failed: {res}")

            # --- FINAL REPORT ---
            gallery_path = str(workspace / "gallery.json")
            self._storage.build_gallery(visuals, gallery_path)

            report_path = str(workspace / "report.json")
            report = self._storage.build_full_report(
                job_id=j_id,
                metadata=metadata,
                transcription=transcription,
                visuals=visuals,
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
                slides_dir=str(workspace / "visuals") if visuals else None,
                ocr_json=str(workspace / "ocr_evidence.json") if ocr_res else None,
                ocr_txt=None,
                timeline_json=timeline.json_path if timeline else None,
                summary_json=summary.json_path if summary else None,
                gallery_json=gallery_path,
                voice_json=voice_result.json_path if voice_result else None,
                report_json=report_path,
            )

            any_failed = any(step.status == ModuleStatus.FAILED for step in job.steps)
            if any_failed:
                job.status = JobStatus.PARTIAL
                job.message = "Pipeline completed with some errors."
            else:
                job.status = JobStatus.COMPLETED
                job.message = "Pipeline completed successfully."

            job.completed_at = datetime.now(timezone.utc).isoformat()
            job.output = output_paths
            job.errors = [step.error for step in job.steps if step.status == ModuleStatus.FAILED and step.error]

            log.info("[{}] Pipeline finished with status {}.", j_id, job.status)
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

    # ---------------------------------------------------------
    # MICRO-PIPELINE ORCHESTRATION
    # ---------------------------------------------------------
    async def _run_audio_pipeline(self, loop, job: JobResponse, audio_path: Path, workspace: Path) -> Tuple[Optional[TranscriptionResult], Optional[VoiceAnalysisResult]]:
        transcription = None
        voice_result = None
        
        if settings.pipeline.transcription:
            transcription = await self._run_in_executor(loop, self._transcribe, job, audio_path, workspace)
            if transcription and transcription.json_path:
                write_json(workspace / "transcript_evidence.json", transcription.model_dump())

            if settings.pipeline.voice_analysis:
                word_count = len(transcription.full_text.split()) if transcription else 0
                voice_result = await self._run_in_executor(loop, self._run_voice_analysis, job, audio_path, workspace, word_count)
                if voice_result and voice_result.json_path:
                    write_json(workspace / "voice_evidence.json", voice_result.model_dump())
                    
        return transcription, voice_result

    async def _run_frame_pipeline(self, loop, job: JobResponse, video_path: Path, workspace: Path) -> Tuple[List, Dict, Dict]:
        frames = []
        if settings.pipeline.frame_extraction:
            frames = await self._run_in_executor(loop, self._extract_keyframes, job, video_path, workspace)
            if frames:
                write_json(workspace / "frames_evidence.json", [{"path": p, "timestamp": t} for p, t in frames])
        
        if not frames:
            if settings.pipeline.ocr:
                self._update_step(job, "ocr", ModuleStatus.SKIPPED, error="No frames extracted")
            self._update_step(job, "diagram_ai", ModuleStatus.SKIPPED, error="No frames extracted")
            return [], {}, {}

        ai_tasks = []
        if settings.pipeline.ocr:
            ai_tasks.append(self._run_in_executor(loop, self._run_ocr_ai, job, frames))
        ai_tasks.append(self._run_in_executor(loop, self._run_diagram_ai, job, frames))

        results = await asyncio.gather(*ai_tasks, return_exceptions=True)
        ocr_res, diag_res = {}, {}
        
        for r in results:
            if isinstance(r, Exception):
                log.error(f"AI task failed: {r}")
            elif isinstance(r, dict):
                # Identify if dictionary is diagram analysis or OCR by checking inner structure
                if any("visual_type" in val for val in r.values()):
                    diag_res = r
                    write_json(workspace / "diagram_evidence.json", diag_res)
                else:
                    ocr_res = r
                    write_json(workspace / "ocr_evidence.json", ocr_res)
                    
        return frames, diag_res, ocr_res


    # ---------------------------------------------------------
    # INDIVIDUAL MODULES
    # ---------------------------------------------------------
    def _init_steps(self, cfg) -> list[ProcessingStep]:
        step_names = ["validation", "preprocessing"]
        if cfg.transcription: step_names.append("transcription")
        if cfg.frame_extraction: step_names.append("frame_extraction")
        if cfg.ocr: step_names.append("ocr")
        if cfg.voice_analysis: step_names.append("voice_analysis")
        step_names.append("diagram_ai")
        step_names.append("visual_assembly")
        if cfg.timeline: step_names.append("timeline")
        if cfg.summary: step_names.append("summary")
        return [ProcessingStep(module_name=name) for name in step_names]

    def _update_step(self, job: JobResponse, module: str, status: ModuleStatus, started_at: Optional[float] = None, error: Optional[str] = None) -> None:
        for step in job.steps:
            if step.module_name == module:
                step.status = status
                if status == ModuleStatus.RUNNING:
                    step.started_at = datetime.now(timezone.utc).isoformat()
                    log.info(f"[STAGE START] {module}")
                elif status in (ModuleStatus.COMPLETED, ModuleStatus.FAILED):
                    step.completed_at = datetime.now(timezone.utc).isoformat()
                    if started_at: step.duration_seconds = round(time.time() - started_at, 2)
                    if status == ModuleStatus.COMPLETED: log.info(f"[STAGE COMPLETED] {module} in {step.duration_seconds}s")
                    elif status == ModuleStatus.FAILED: log.error(f"[STAGE FAILED] {module} - Reason: {error}")
                if error: step.error = error
                break

    async def _run_in_executor(self, loop, func, *args):
        return await loop.run_in_executor(self._executor, func, *args)

    async def _run_validation(self, job: JobResponse, video_path: Path) -> VideoMetadata:
        start = time.time()
        self._update_step(job, "validation", ModuleStatus.RUNNING)
        result = self._validator.validate(video_path)
        if not result.validation_passed or not result.metadata:
            self._update_step(job, "validation", ModuleStatus.FAILED, started_at=start, error="; ".join(result.errors))
            raise ValidationError(f"Video validation failed: {'; '.join(result.errors)}")
        self._update_step(job, "validation", ModuleStatus.COMPLETED, started_at=start)
        job.warnings.extend(result.warnings)
        return result.metadata

    async def _run_preprocessing(self, job: JobResponse, video_path: Path, job_id: str, metadata: VideoMetadata) -> PreprocessingResult:
        start = time.time()
        self._update_step(job, "preprocessing", ModuleStatus.RUNNING)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self._executor, self._preprocessor.process, video_path, job_id, metadata)
        self._update_step(job, "preprocessing", ModuleStatus.COMPLETED, started_at=start)
        return result

    def _transcribe(self, job: JobResponse, audio_path: Path, workspace: Path) -> TranscriptionResult:
        start = time.time()
        self._update_step(job, "transcription", ModuleStatus.RUNNING)
        try:
            result = self._transcriber.transcribe(audio_path, workspace)
            self._update_step(job, "transcription", ModuleStatus.COMPLETED, started_at=start)
            return result
        except Exception as exc:
            self._update_step(job, "transcription", ModuleStatus.FAILED, started_at=start, error=str(exc))
            raise

    def _extract_keyframes(self, job: JobResponse, video_path: Path, workspace: Path) -> List[Tuple[str, float]]:
        start = time.time()
        self._update_step(job, "frame_extraction", ModuleStatus.RUNNING)
        try:
            output_dir = str(workspace / "visuals")
            frames = extract_representative_frames(str(video_path), output_dir)
            self._update_step(job, "frame_extraction", ModuleStatus.COMPLETED, started_at=start)
            return frames
        except Exception as exc:
            self._update_step(job, "frame_extraction", ModuleStatus.FAILED, started_at=start, error=str(exc))
            raise
            
    def _run_ocr_ai(self, job: JobResponse, frames: List[Tuple[str, float]]) -> Dict[str, dict]:
        start = time.time()
        self._update_step(job, "ocr", ModuleStatus.RUNNING)
        try:
            results = run_ocr_ai(frames)
            self._update_step(job, "ocr", ModuleStatus.COMPLETED, started_at=start)
            return results
        except Exception as exc:
            self._update_step(job, "ocr", ModuleStatus.FAILED, started_at=start, error=str(exc))
            raise

    def _run_diagram_ai(self, job: JobResponse, frames: List[Tuple[str, float]]) -> Dict[str, dict]:
        start = time.time()
        self._update_step(job, "diagram_ai", ModuleStatus.RUNNING)
        try:
            results = run_diagram_ai(frames)
            self._update_step(job, "diagram_ai", ModuleStatus.COMPLETED, started_at=start)
            return results
        except Exception as exc:
            self._update_step(job, "diagram_ai", ModuleStatus.FAILED, started_at=start, error=str(exc))
            raise

    def _assemble_visuals(self, job: JobResponse, job_id: str, frames: List[Tuple[str, float]], diag_res: Dict, ocr_res: Dict, transcription: Optional[TranscriptionResult], workspace: Path) -> List[SlideDTO]:
        start = time.time()
        self._update_step(job, "visual_assembly", ModuleStatus.RUNNING)
        try:
            transcript_data = transcription.model_dump().get("segments", []) if transcription else []
            db = SessionLocal()
            try:
                visuals, db_error_count = assemble_visual_evidence(job_id, frames, diag_res, ocr_res, transcript_data, db)
            finally:
                db.close()
            
            if db_error_count > 0:
                self._update_step(job, "visual_assembly", ModuleStatus.FAILED, started_at=start, error=f"{db_error_count} visual(s) failed DB indexing")
            else:
                self._update_step(job, "visual_assembly", ModuleStatus.COMPLETED, started_at=start)
            return visuals
        except Exception as exc:
            self._update_step(job, "visual_assembly", ModuleStatus.FAILED, started_at=start, error=str(exc))
            raise

    def _run_voice_analysis(self, job: JobResponse, audio_path: Path, workspace: Path, word_count: int) -> VoiceAnalysisResult:
        start = time.time()
        self._update_step(job, "voice_analysis", ModuleStatus.RUNNING)
        try:
            result = self._voice_analyzer.analyze(audio_path, workspace, word_count)
            self._update_step(job, "voice_analysis", ModuleStatus.COMPLETED, started_at=start)
            return result
        except Exception as exc:
            self._update_step(job, "voice_analysis", ModuleStatus.FAILED, started_at=start, error=str(exc))
            raise

    def _build_timeline(self, job: JobResponse, transcription: Optional[TranscriptionResult], visuals: Optional[list[SlideDTO]], output_path: str, duration: float) -> Timeline:
        start = time.time()
        self._update_step(job, "timeline", ModuleStatus.RUNNING)
        try:
            result = self._timeline_builder.build(transcription, visuals, output_path, duration)
            self._update_step(job, "timeline", ModuleStatus.COMPLETED, started_at=start)
            return result
        except Exception as exc:
            self._update_step(job, "timeline", ModuleStatus.FAILED, started_at=start, error=str(exc))
            raise

    def _generate_summary(self, job: JobResponse, transcription: Optional[TranscriptionResult], visuals: Optional[list[SlideDTO]], output_path: str, visuals_count: int = 0) -> TeachingSummary:
        start = time.time()
        self._update_step(job, "summary", ModuleStatus.RUNNING)
        try:
            result = self._summary_generator.generate(transcription, visuals, output_path, visuals_count)
            self._update_step(job, "summary", ModuleStatus.COMPLETED, started_at=start)
            return result
        except Exception as exc:
            self._update_step(job, "summary", ModuleStatus.FAILED, started_at=start, error=str(exc))
            raise
