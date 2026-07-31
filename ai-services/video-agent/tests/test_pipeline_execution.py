import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.pipeline_orchestrator import PipelineOrchestrator
from app.models.job import JobStatus
from app.models.validation import VideoMetadata
from app.preprocessing.video_preprocessor import PreprocessingResult

@pytest.mark.asyncio
async def test_pipeline_continues_on_ocr_failure():
    orchestrator = PipelineOrchestrator()
    job_id = str(uuid.uuid4())
    
    with patch.object(orchestrator, "_run_validation", new_callable=AsyncMock) as mock_val, \
         patch.object(orchestrator, "_run_preprocessing", new_callable=AsyncMock) as mock_prep, \
         patch.object(orchestrator, "_run_in_executor", new_callable=AsyncMock) as mock_exec, \
         patch("app.config.settings.settings.pipeline") as mock_cfg:
        
        mock_val.return_value = VideoMetadata(
            duration_seconds=10.0,
            has_audio=True,
            has_video=True,
            video_codec="h264",
            resolution="1920x1080",
            mime_type="video/mp4"
        )
        mock_prep.return_value = PreprocessingResult(
            audio_path="test.mp3",
            normalized_video_path="test.mp4",
            metadata_path="test.json"
        )
        
        # Simulate an exception in OCR by configuring _run_in_executor
        async def mock_exec_side_effect(loop, func, *args):
            if func == orchestrator._run_ocr:
                return None  # _run_ocr returns None on failure now
            return MagicMock()
            
        mock_exec.side_effect = mock_exec_side_effect
        
        job = await orchestrator.process_video("dummy.mp4", job_id)
        
        assert job.status == JobStatus.COMPLETED
        # Ensure that generate summary was called despite OCR returning None
        summary_calls = [c for c in mock_exec.call_args_list if c[0][1] == orchestrator._generate_summary]
        assert len(summary_calls) == 1
