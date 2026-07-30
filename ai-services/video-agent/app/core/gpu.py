"""
FacultyIQ Video Evidence Extraction Service — GPU Detection Utility.

Auto-detects CUDA availability for Faster-Whisper, FFmpeg NVDEC/NVENC, and OCR.
Always falls back to CPU gracefully — never fails if GPU is unavailable.
"""

from dataclasses import dataclass
from typing import Optional

from loguru import logger


@dataclass(frozen=True)
class GPUCapabilities:
    """Describes detected GPU capabilities."""

    cuda_available: bool
    device_name: Optional[str]
    compute_type: str
    ffmpeg_hwaccel: Optional[str]


def detect_gpu(prefer_cuda: bool = True) -> GPUCapabilities:
    """
    Detects GPU availability for Whisper (CTranslate2) and FFmpeg.

    Returns a GPUCapabilities dataclass with resolved settings.
    Falls back to CPU with int8 compute if CUDA is unavailable.
    """
    cuda_available = False
    device_name: Optional[str] = None
    compute_type = "int8"
    ffmpeg_hwaccel: Optional[str] = None

    if not prefer_cuda:
        logger.info("GPU preference disabled; using CPU (int8).")
        return GPUCapabilities(
            cuda_available=False,
            device_name=None,
            compute_type="int8",
            ffmpeg_hwaccel=None,
        )

    try:
        import ctranslate2

        supported = ctranslate2.get_supported_compute_types("cuda")
        if supported and len(supported) > 0:
            cuda_available = True
            compute_type = "float16" if "float16" in supported else supported[0]
            logger.info(
                "CTranslate2 CUDA detected. Supported compute types: {}",
                supported,
            )
    except Exception as exc:
        logger.debug("CTranslate2 CUDA detection failed: {}", exc)

    if cuda_available:
        try:
            import torch

            if torch.cuda.is_available():
                device_name = torch.cuda.get_device_name(0)
                logger.info("CUDA GPU detected: {}", device_name)
        except ImportError:
            logger.debug("PyTorch not installed; GPU name unavailable.")
        except Exception as exc:
            logger.debug("torch.cuda detection error: {}", exc)

    if cuda_available:
        try:
            import subprocess

            result = subprocess.run(
                ["ffmpeg", "-hwaccels"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if "cuda" in result.stdout.lower():
                ffmpeg_hwaccel = "cuda"
                logger.info("FFmpeg CUDA hardware acceleration available.")
            elif "nvdec" in result.stdout.lower():
                ffmpeg_hwaccel = "cuda"
        except Exception as exc:
            logger.debug("FFmpeg hwaccel detection failed: {}", exc)

    if not cuda_available:
        logger.info("No CUDA GPU detected; falling back to CPU (int8).")

    return GPUCapabilities(
        cuda_available=cuda_available,
        device_name=device_name,
        compute_type=compute_type,
        ffmpeg_hwaccel=ffmpeg_hwaccel,
    )


_cached_capabilities: Optional[GPUCapabilities] = None


def get_gpu_capabilities(prefer_cuda: bool = True) -> GPUCapabilities:
    """Returns cached GPU capabilities, detecting only once."""
    global _cached_capabilities
    if _cached_capabilities is None:
        _cached_capabilities = detect_gpu(prefer_cuda=prefer_cuda)
    return _cached_capabilities
