"""
FacultyIQ Coding Intelligence Agent — Structured Logging.

Configures Loguru with module-specific log sinks so each pipeline stage
writes to its own log file alongside a master log.
"""

import sys
from pathlib import Path

from loguru import logger

from app.config.settings import settings
from app.utils.file_utils import ensure_directory

_LOGGING_INITIALIZED = False

MODULE_LOG_MAP = {
    "sandbox": "sandbox.log",
    "compilation": "compilation.log",
    "test_runner": "test_runner.log",
    "complexity": "complexity.log",
    "static_analysis": "static_analysis.log",
    "explanation": "explanation.log",
    "viva": "viva.log",
    "debugging": "debugging.log",
    "evidence": "evidence.log",
    "question_bank": "question_bank.log",
    "pipeline": "pipeline.log",
    "api": "api.log",
}

_CONSOLE_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

_FILE_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | "
    "{name}:{function}:{line} - "
    "{message}"
)


def _module_filter(module_name: str):
    """Returns a Loguru filter that only passes records bound to the given module."""
    def _filter(record: dict) -> bool:
        return record.get("extra", {}).get("module", "") == module_name
    return _filter


def setup_logging() -> None:
    """Configures Loguru logger sinks for stdout, master log, and per-module log files."""
    global _LOGGING_INITIALIZED
    if _LOGGING_INITIALIZED:
        return
    _LOGGING_INITIALIZED = True

    logger.remove()

    log_dir = ensure_directory(settings.base_dir / settings.storage.logs_dir)

    logger.add(
        sys.stdout,
        format=_CONSOLE_FORMAT,
        level=settings.logging.level,
        enqueue=True,
    )

    master_log = log_dir / "coding_agent.log"
    logger.add(
        str(master_log),
        format=_FILE_FORMAT,
        rotation=settings.logging.rotation,
        retention=settings.logging.retention,
        level="DEBUG",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    if settings.logging.enable_module_logs:
        for module_name, filename in MODULE_LOG_MAP.items():
            module_log_path = log_dir / filename
            logger.add(
                str(module_log_path),
                format=_FILE_FORMAT,
                rotation=settings.logging.rotation,
                retention=settings.logging.retention,
                level="DEBUG",
                enqueue=True,
                backtrace=True,
                diagnose=True,
                filter=_module_filter(module_name),
            )

    logger.info("Logging initialized. Master log → {}", master_log)


def get_module_logger(module_name: str):
    """Returns a logger bound to a specific module name for per-module log routing."""
    return logger.bind(module=module_name)
