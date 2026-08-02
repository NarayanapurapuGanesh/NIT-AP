"""
FacultyIQ Coding Intelligence Agent — Configuration Settings.

Loads configuration from config.yaml with Pydantic v2 validation.
Each subsystem has its own settings class for strict typing.
"""

from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    """Application-level metadata."""
    name: str = "FacultyIQ Coding Intelligence Agent"
    version: str = "1.0.0"
    environment: str = "development"


class ServerSettings(BaseModel):
    """HTTP server configuration."""
    host: str = "0.0.0.0"
    port: int = 8015
    workers: int = 1
    reload: bool = True


class StorageSettings(BaseModel):
    """File storage paths relative to project root."""
    temp_dir: str = "temp"
    output_dir: str = "output"
    logs_dir: str = "logs"
    uploads_dir: str = "temp/uploads"


class SandboxSettings(BaseModel):
    """Secure code execution sandbox configuration."""
    mode: str = "auto"
    timeout_seconds: int = 15
    memory_limit_mb: int = 256
    cpu_limit: float = 1.0
    max_output_bytes: int = 65536
    cleanup_containers: bool = True


class OllamaSettings(BaseModel):
    """AI Orchestrator connection settings."""
    orchestrator_url: str = "http://localhost:8010"
    agent_name: str = "coding"
    timeout_seconds: int = 120


class PipelineSettings(BaseModel):
    """Assessment pipeline configuration."""
    max_questions_per_session: int = 10
    default_difficulty: str = "medium"
    adaptive_enabled: bool = True
    explanation_weight: float = 0.15
    viva_weight: float = 0.10
    correctness_weight: float = 0.35
    complexity_weight: float = 0.15
    quality_weight: float = 0.10
    debugging_weight: float = 0.15


class LoggingSettings(BaseModel):
    """Logging configuration."""
    level: str = "DEBUG"
    rotation: str = "10 MB"
    retention: str = "14 days"
    enable_module_logs: bool = True


class Settings(BaseModel):
    """Root configuration aggregating all subsystem settings."""
    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent
    )
    app: AppSettings = Field(default_factory=AppSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    sandbox: SandboxSettings = Field(default_factory=SandboxSettings)
    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    pipeline: PipelineSettings = Field(default_factory=PipelineSettings)
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
        "sandbox": SandboxSettings,
        "ollama": OllamaSettings,
        "pipeline": PipelineSettings,
        "logging": LoggingSettings,
    }
    for key, model_cls in field_mapping.items():
        section = raw.get(key)
        if isinstance(section, dict):
            kwargs[key] = model_cls(**section)
    return Settings(**kwargs)


settings: Settings = _build_settings()
