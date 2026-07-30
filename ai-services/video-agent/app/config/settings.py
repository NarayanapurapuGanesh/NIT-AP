"""
FacultyIQ Video Evidence Extraction Service — Configuration Settings.

Loads configuration from config.yaml with environment variable overrides.
Each subsystem has its own Pydantic v2 settings class for strict validation.
"""

from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    """Application-level metadata."""

    name: str = "FacultyIQ Video Evidence Extraction Service"
    version: str = "2.0.0"
    environment: str = "development"


class ServerSettings(BaseModel):
    """HTTP server configuration."""

    host: str = "0.0.0.0"
    port: int = 8005
    workers: int = 1
    reload: bool = True


class StorageSettings(BaseModel):
    """File storage paths relative to project root."""

    temp_dir: str = "temp"
    output_dir: str = "output"
    logs_dir: str = "logs"
    uploads_dir: str = "temp/uploads"


class ValidationSettings(BaseModel):
    """Video validation constraints."""

    allowed_extensions: List[str] = Field(
        default=[".mp4", ".mov", ".avi", ".mkv", ".webm"]
    )
    allowed_mime_types: List[str] = Field(
        default=[
            "video/mp4",
            "video/quicktime",
            "video/x-msvideo",
            "video/x-matroska",
            "video/webm",
        ]
    )
    max_file_size_mb: int = 500
    min_duration_seconds: float = 10.0
    max_duration_seconds: float = 7200.0


class WhisperSettings(BaseModel):
    """Faster-Whisper transcription engine configuration."""

    model_size: str = "small"
    device: str = "auto"
    compute_type: str = "auto"
    beam_size: int = 5
    language: str = "en"
    word_timestamps: bool = True


class SceneDetectionSettings(BaseModel):
    """PySceneDetect configuration."""

    threshold: float = 27.0
    min_scene_duration: float = 2.0
    max_keyframes_per_scene: int = 1
    output_format: str = "jpg"
    output_quality: int = 95


class OCRSettings(BaseModel):
    """Tesseract OCR configuration."""

    language: str = "eng"
    psm: int = 6
    oem: int = 3
    min_confidence: float = 30.0
    preprocessing: bool = True


class VoiceSettings(BaseModel):
    """Voice analysis configuration."""

    enabled: bool = False
    sample_rate: int = 16000
    hop_length: int = 512
    min_pitch_hz: float = 50.0
    max_pitch_hz: float = 500.0


class PipelineSettings(BaseModel):
    """Pipeline module toggles and execution configuration."""

    transcription: bool = True
    frame_extraction: bool = True
    ocr: bool = True
    timeline: bool = True
    summary: bool = True
    voice_analysis: bool = False
    parallel_execution: bool = True
    max_workers: int = 4


class GPUSettings(BaseModel):
    """GPU acceleration configuration."""

    enabled: bool = True
    prefer_cuda: bool = True
    ffmpeg_hwaccel: str = "auto"


class LoggingSettings(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    rotation: str = "10 MB"
    retention: str = "14 days"
    format: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "{extra[module]} | <level>{message}</level>"
    )
    enable_module_logs: bool = True


class Settings(BaseModel):
    """Root configuration aggregating all subsystem settings."""

    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent
    )
    app: AppSettings = Field(default_factory=AppSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    validation: ValidationSettings = Field(default_factory=ValidationSettings)
    whisper: WhisperSettings = Field(default_factory=WhisperSettings)
    scene_detection: SceneDetectionSettings = Field(
        default_factory=SceneDetectionSettings
    )
    ocr: OCRSettings = Field(default_factory=OCRSettings)
    voice: VoiceSettings = Field(default_factory=VoiceSettings)
    pipeline: PipelineSettings = Field(default_factory=PipelineSettings)
    gpu: GPUSettings = Field(default_factory=GPUSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)


def _load_yaml_config() -> dict:
    """Loads configuration from config.yaml alongside this module."""
    config_path = Path(__file__).resolve().parent / "config.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def _build_settings() -> Settings:
    """Constructs Settings from YAML, merging nested sections."""
    raw = _load_yaml_config()

    kwargs: dict = {}
    field_mapping = {
        "app": AppSettings,
        "server": ServerSettings,
        "storage": StorageSettings,
        "validation": ValidationSettings,
        "whisper": WhisperSettings,
        "scene_detection": SceneDetectionSettings,
        "ocr": OCRSettings,
        "voice": VoiceSettings,
        "pipeline": PipelineSettings,
        "gpu": GPUSettings,
        "logging": LoggingSettings,
    }

    for key, model_cls in field_mapping.items():
        section = raw.get(key)
        if isinstance(section, dict):
            kwargs[key] = model_cls(**section)

    return Settings(**kwargs)


settings: Settings = _build_settings()
