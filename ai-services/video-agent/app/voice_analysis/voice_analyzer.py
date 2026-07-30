"""
FacultyIQ Video Evidence Extraction Service — Voice Analyzer (Module 10).

Optional voice metrics extraction using librosa and scipy.
Computes speech rate, pause ratio, average pitch, volume stability, noise level.
"""

from pathlib import Path
from typing import Optional, Union

from app.config.settings import settings
from app.core.logging import get_module_logger
from app.models.voice import VoiceAnalysisResult, VoiceMetrics
from app.utils.file_utils import write_json

log = get_module_logger("voice")


class VoiceAnalyzer:
    """Extracts voice metrics from audio using librosa and scipy signal processing."""

    def __init__(self, enabled: Optional[bool] = None) -> None:
        self._enabled = enabled if enabled is not None else settings.voice.enabled
        self._sample_rate = settings.voice.sample_rate
        self._hop_length = settings.voice.hop_length
        self._min_pitch = settings.voice.min_pitch_hz
        self._max_pitch = settings.voice.max_pitch_hz

    def analyze(
        self,
        audio_path: Union[str, Path],
        output_dir: Union[str, Path],
        word_count: int = 0,
    ) -> VoiceAnalysisResult:
        """Analyzes audio and returns voice metrics."""
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / "voice_analysis.json"

        if not self._enabled:
            log.info("Voice analysis is disabled by configuration.")
            result = VoiceAnalysisResult(
                enabled=False, metrics=None, json_path=None
            )
            return result

        a_path = Path(audio_path).resolve()
        if not a_path.exists():
            log.warning("Audio file not found for voice analysis: {}", a_path)
            result = VoiceAnalysisResult(
                enabled=True, metrics=None, json_path=None
            )
            return result

        log.info("Starting voice analysis for: {}", a_path.name)

        try:
            metrics = self._compute_metrics(a_path, word_count)

            result = VoiceAnalysisResult(
                enabled=True,
                metrics=metrics,
                json_path=str(json_path),
            )
            write_json(json_path, result)

            log.info(
                "Voice analysis complete: {:.1f} wpm, {:.1f} Hz avg pitch",
                metrics.speech_rate_wpm,
                metrics.average_pitch_hz,
            )
            return result

        except Exception as exc:
            log.error("Voice analysis failed: {}", exc)
            return VoiceAnalysisResult(
                enabled=True, metrics=None, json_path=None
            )

    def _compute_metrics(self, audio_path: Path, word_count: int) -> VoiceMetrics:
        """Computes all voice metrics from the audio file."""
        import numpy as np
        import librosa

        y, sr = librosa.load(str(audio_path), sr=self._sample_rate)
        duration = librosa.get_duration(y=y, sr=sr)

        speech_rate = (word_count / duration * 60.0) if duration > 0 and word_count > 0 else 0.0

        rms = librosa.feature.rms(y=y, hop_length=self._hop_length)[0]
        silence_threshold = np.mean(rms) * 0.1
        silent_frames = np.sum(rms < silence_threshold)
        pause_ratio = float(silent_frames / len(rms)) if len(rms) > 0 else 0.0

        pitches, magnitudes = librosa.piptrack(
            y=y, sr=sr, hop_length=self._hop_length
        )
        valid_pitches = pitches[
            (pitches > self._min_pitch) & (pitches < self._max_pitch)
        ]
        avg_pitch = float(np.mean(valid_pitches)) if len(valid_pitches) > 0 else 0.0

        volume_stability = float(np.std(rms)) if len(rms) > 0 else 0.0

        noise_rms = np.percentile(rms, 10) if len(rms) > 0 else 0.0
        noise_db = float(20 * np.log10(noise_rms + 1e-10))

        confidence = 1.0
        if duration < 30:
            confidence *= 0.5
        if word_count < 10:
            confidence *= 0.5
        if len(valid_pitches) < 100:
            confidence *= 0.7

        return VoiceMetrics(
            speech_rate_wpm=round(speech_rate, 1),
            pause_ratio=round(pause_ratio, 3),
            average_pitch_hz=round(avg_pitch, 1),
            volume_stability=round(volume_stability, 6),
            noise_level_db=round(noise_db, 1),
            confidence=round(min(confidence, 1.0), 2),
        )
