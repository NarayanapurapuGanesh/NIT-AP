import uuid
from pathlib import Path
from typing import Dict, Optional, Union
from loguru import logger

from app.core.exceptions import ValidationError
from app.models.job import JobResponse, JobStatus, PipelineResult
from app.models.validation import ValidationResult
from app.preprocessing.video_preprocessor import VideoPreprocessor
from app.transcription.whisper_transcriber import WhisperTranscriber
from app.validators.video_validator import VideoValidator


class VideoPipelineService:
    """Service orchestrating Phase 1, Phase 2, and Phase 3 video evaluation pipeline."""

    def __init__(
        self,
        validator: Optional[VideoValidator] = None,
        preprocessor: Optional[VideoPreprocessor] = None,
        transcriber: Optional[WhisperTranscriber] = None,
    ) -> None:
        self.validator = validator or VideoValidator()
        self.preprocessor = preprocessor or VideoPreprocessor()
        self.transcriber = transcriber or WhisperTranscriber()
        self.job_store: Dict[str, JobResponse] = {}

    def validate_video(self, video_path: Union[str, Path]) -> ValidationResult:
        """Executes Phase 1 video upload validation."""
        v_path = Path(video_path).resolve()
        logger.info(f"Orchestrating Phase 1 validation for {v_path.name}")
        return self.validator.validate(v_path)

    def process_pipeline(
        self,
        video_path: Union[str, Path],
        job_id: Optional[str] = None,
    ) -> JobResponse:
        """Executes Phase 1 validation, Phase 2 preprocessing, and Phase 3 transcription sequentially."""
        j_id = job_id or str(uuid.uuid4())
        v_path = Path(video_path).resolve()

        logger.info(f"[{j_id}] Starting Video Evaluation Pipeline for {v_path.name}")
        job_resp = JobResponse(
            job_id=j_id,
            status=JobStatus.PROCESSING,
            message="Pipeline execution started.",
        )
        self.job_store[j_id] = job_resp

        try:
            # Phase 1: Validation
            val_res = self.validator.validate(v_path)
            if not val_res.validationPassed or not val_res.metadata:
                job_resp.status = JobStatus.FAILED
                job_resp.message = "Phase 1 validation failed."
                job_resp.errors = val_res.errors
                return job_resp

            video_metadata = val_res.metadata

            # Phase 2: Preprocessing
            prep_res = self.preprocessor.process(v_path, job_id=j_id, metadata=video_metadata)

            # Phase 3: Transcription
            out_base_dir = Path(prep_res.metadata_cache_path).parent
            trans_res = self.transcriber.transcribe(prep_res.audio_path, out_base_dir)

            pipeline_res = PipelineResult(
                video_metadata=video_metadata,
                preprocessing=prep_res,
                transcription=trans_res,
            )

            job_resp.status = JobStatus.COMPLETED
            job_resp.message = "Pipeline execution completed successfully."
            job_resp.result = pipeline_res
            job_resp.errors = []
            logger.info(f"[{j_id}] Video Evaluation Pipeline completed successfully.")
            return job_resp

        except Exception as e:
            logger.error(f"[{j_id}] Pipeline execution failed: {e}")
            job_resp.status = JobStatus.FAILED
            job_resp.message = f"Pipeline failed: {str(e)}"
            job_resp.errors = [str(e)]
            return job_resp

    def get_job_status(self, job_id: str) -> JobResponse:
        """Retrieves pipeline execution status for job_id."""
        if job_id not in self.job_store:
            return JobResponse(
                job_id=job_id,
                status=JobStatus.FAILED,
                message=f"Job '{job_id}' not found.",
                errors=[f"Job ID '{job_id}' does not exist."],
            )
        return self.job_store[job_id]
