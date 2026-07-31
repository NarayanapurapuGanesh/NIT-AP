import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.pipeline_orchestrator import PipelineOrchestrator
from app.models.job import JobStatus, ModuleStatus
from app.models.validation import VideoMetadata
from app.preprocessing.video_preprocessor import PreprocessingResult

from app.models.transcription import TranscriptionResult

@pytest.mark.asyncio
async def test_pipeline_partial_status_on_visual_assembly_failure():
    orchestrator = PipelineOrchestrator()
    job_id = str(uuid.uuid4())
    
    with patch.object(orchestrator, "_run_validation", new_callable=AsyncMock) as mock_val, \
         patch.object(orchestrator, "_run_preprocessing", new_callable=AsyncMock) as mock_prep, \
         patch.object(orchestrator, "_run_in_executor", new_callable=AsyncMock) as mock_exec, \
         patch.object(orchestrator._storage, "build_full_report") as mock_report, \
         patch.object(orchestrator._storage, "build_gallery") as mock_gallery, \
         patch("app.utils.file_utils.write_json"), \
         patch("app.config.settings.settings.pipeline") as mock_cfg:
        
        mock_val.return_value = VideoMetadata(
            filename="dummy.mp4",
            format="mp4",
            file_size_bytes=1000,
            file_size_mb=1.0,
            width=1920,
            height=1080,
            fps=30.0,
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
            metadata_path="test.json",
            workspace_dir="workspace",
            preview_path="preview.mp4"
        )
        
        # Simulate an exception in visual assembly
        async def mock_exec_side_effect(loop, func, *args):
            job = args[0]
            if func == orchestrator._assemble_visuals:
                orchestrator._update_step(job, "visual_assembly", ModuleStatus.FAILED, error="Mocked visual assembly failure")
                raise RuntimeError("Mocked visual assembly failure")
            # For _extract_keyframes, return some fake frames so visual_assembly is called
            if func == orchestrator._extract_keyframes:
                return [("frame1.jpg", 1.0)]
            if func == orchestrator._run_diagram_ai:
                return {"frame1.jpg": {"visual_type": "Whiteboard"}}
            if func == orchestrator._run_ocr_ai:
                return {"frame1.jpg": {"raw_text": "hello"}}
            if func == orchestrator._transcribe:
                return TranscriptionResult(full_text="test", segments=[], json_path="t.json", txt_path="t.txt")
            if func == orchestrator._run_voice_analysis:
                return None
            return MagicMock()
            
        mock_exec.side_effect = mock_exec_side_effect
        
        job = await orchestrator.process_video("dummy.mp4", job_id)
        
        assert job.status == JobStatus.PARTIAL
        assert any("Mocked visual assembly failure" in str(e) for e in job.errors)
        
        # Ensure downstream summarize was called despite visual assembly failing
        summary_calls = [c for c in mock_exec.call_args_list if c[0][1] == orchestrator._generate_summary]
        assert len(summary_calls) == 1
