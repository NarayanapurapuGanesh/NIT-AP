"""
FacultyIQ Video Evidence Extraction Service — FFmpeg Wrapper.

Thread-safe wrapper around FFmpeg CLI with GPU acceleration support.
"""

import subprocess
from typing import List, Optional

from app.core.exceptions import PreprocessingError
from app.core.gpu import get_gpu_capabilities
from app.core.logging import get_module_logger

log = get_module_logger("preprocessing")


class FFmpegWrapper:
    """Executes FFmpeg commands with optional GPU hardware acceleration."""

    def __init__(self, hwaccel: Optional[str] = None) -> None:
        gpu = get_gpu_capabilities()
        self._hwaccel = hwaccel or gpu.ffmpeg_hwaccel

    def run_command(
        self,
        args: List[str],
        description: str = "FFmpeg command",
        timeout: int = 600,
    ) -> str:
        """Executes an FFmpeg command with logging and error handling."""
        cmd = ["ffmpeg"] + args
        log.debug("Executing FFmpeg [{}]: {}", description, " ".join(cmd))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout,
            )
            log.info("FFmpeg [{}] completed successfully.", description)
            return result.stdout
        except subprocess.TimeoutExpired:
            log.error("FFmpeg [{}] timed out after {}s.", description, timeout)
            raise PreprocessingError(
                f"FFmpeg timed out during {description} after {timeout}s."
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr or "No stderr output"
            log.error("FFmpeg [{}] failed: {}", description, stderr[:500])
            raise PreprocessingError(
                f"FFmpeg error during {description}: {stderr[:500]}"
            ) from exc

    def get_hwaccel_input_args(self) -> List[str]:
        """Returns FFmpeg input args for GPU-accelerated decoding, if available."""
        if self._hwaccel == "cuda":
            return ["-hwaccel", "cuda", "-hwaccel_output_format", "cuda"]
        return []

    def get_hwaccel_output_args(self) -> List[str]:
        """Returns FFmpeg output encoding args for GPU, if available."""
        if self._hwaccel == "cuda":
            return ["-c:v", "h264_nvenc"]
        return ["-c:v", "libx264"]
