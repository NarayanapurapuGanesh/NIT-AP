"""
FacultyIQ Video Evidence Extraction Service — Whisper Transcriber (Module 3).

Transcribes audio using Faster-Whisper with GPU acceleration and CPU fallback.
Produces transcript.json and transcript.txt with word-level timestamps.
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

from app.config.settings import settings
from app.core.exceptions import TranscriptionError
from app.core.gpu import get_gpu_capabilities
from app.core.logging import get_module_logger
from app.models.transcription import Segment, TranscriptionResult, WordTimestamp
from app.utils.file_utils import write_json, write_text

log = get_module_logger("transcription")


class WhisperTranscriber:
    """Faster-Whisper speech transcriber with CTranslate2 GPU acceleration."""

    def __init__(
        self,
        model_size: Optional[str] = None,
        device: Optional[str] = None,
        compute_type: Optional[str] = None,
    ) -> None:
        self._model_size = model_size or settings.whisper.model_size
        self._requested_device = device or settings.whisper.device
        self._requested_compute_type = compute_type or settings.whisper.compute_type
        self._beam_size = settings.whisper.beam_size
        self._language = settings.whisper.language
        self._word_timestamps = settings.whisper.word_timestamps
        self._model = None

    def _resolve_device(self) -> Tuple[str, str]:
        """Resolves device and compute type using GPU detection."""
        gpu = get_gpu_capabilities(prefer_cuda=settings.gpu.prefer_cuda)

        device = self._requested_device
        compute_type = self._requested_compute_type

        if device in ("auto", "cuda"):
            if gpu.cuda_available:
                device = "cuda"
                compute_type = gpu.compute_type if compute_type == "auto" else compute_type
            else:
                log.warning("CUDA not available; falling back to CPU (int8).")
                device = "cpu"
                compute_type = "int8"

        if device == "cpu" and compute_type == "float16":
            compute_type = "int8"

        log.info("Whisper device: {} (compute_type: {})", device, compute_type)
        return device, compute_type

    def _load_model(self):
        """Lazy-loads the Whisper model."""
        if self._model is not None:
            return self._model

        import whisper

        device, compute_type = self._resolve_device()
        log.info(
            "Loading OpenAI-Whisper model '{}' on {}...",
            self._model_size, device,
        )

        try:
            self._model = whisper.load_model(self._model_size, device=device)
            log.info("Whisper model loaded successfully.")
            return self._model
        except Exception as exc:
            log.error(
                "Failed to load Whisper on {}: {}. Retrying on CPU...",
                device, exc,
            )
            self._model = whisper.load_model(self._model_size, device="cpu")
            return self._model

    def transcribe(
        self,
        audio_path: Union[str, Path],
        output_dir: Union[str, Path],
    ) -> TranscriptionResult:
        """Transcribes audio and generates transcript.json and transcript.txt."""
        a_path = Path(audio_path).resolve()
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        if not a_path.exists():
            raise TranscriptionError(
                f"Audio file does not exist: {a_path}"
            )

        log.info("Transcribing audio: {}", a_path.name)

        model = self._load_model()
        # openai-whisper transcribe returns a dict
        result_dict = model.transcribe(
            str(a_path),
            language=self._language,
            word_timestamps=self._word_timestamps,
        )
        
        segments_raw = result_dict.get("segments", [])

        segments: List[Segment] = []
        full_text_parts: List[str] = []

        for idx, seg in enumerate(segments_raw):
            text = seg.get("text", "").strip()
            if not text:
                continue

            full_text_parts.append(text)

            words: List[WordTimestamp] = []
            if "words" in seg and seg["words"]:
                for w in seg["words"]:
                    words.append(
                        WordTimestamp(
                            word=w.get("word", "").strip(),
                            start=round(w.get("start", 0.0), 3),
                            end=round(w.get("end", 0.0), 3),
                            probability=round(w.get("probability", 1.0), 4),
                        )
                    )

            avg_conf = 0.0
            if words:
                avg_conf = sum(w.probability for w in words) / len(words)
            elif "avg_logprob" in seg:
                import math
                avg_conf = math.exp(seg["avg_logprob"])

            segments.append(
                Segment(
                    id=idx + 1,
                    start=round(seg.get("start", 0.0), 2),
                    end=round(seg.get("end", 0.0), 2),
                    text=text,
                    confidence=round(avg_conf, 4),
                    speaker=None,
                    words=words,
                )
            )

        full_text = " ".join(full_text_parts)
        # openai-whisper doesn't return duration directly in the same way, we can infer from the last segment
        duration = segments[-1].end if segments else 0.0

        json_path = out_dir / "transcript.json"
        txt_path = out_dir / "transcript.txt"

        result = TranscriptionResult(
            full_text=full_text,
            segments=segments,
            language=result_dict.get("language", self._language),
            model_used=self._model_size,
            duration_seconds=round(duration, 2),
            json_path=str(json_path),
            txt_path=str(txt_path),
        )

        write_json(json_path, result)
        write_text(txt_path, full_text)

        log.info(
            "Transcription complete: {} segments, {} words, {:.1f}s duration",
            len(segments),
            len(full_text.split()),
            duration,
        )
        return result
