"""
FacultyIQ Coding Intelligence Agent — Sandbox Manager.

Orchestrates code execution by selecting the appropriate executor
(Docker for security, subprocess as fallback).
"""

from app.config.settings import settings
from app.core.logging import get_module_logger
from app.models.sandbox import ExecutionRequest, ExecutionResult
from app.sandbox.docker_executor import DockerExecutor
from app.sandbox.subprocess_executor import SubprocessExecutor

log = get_module_logger("sandbox")


class SandboxManager:
    """
    Manages secure code execution with automatic mode selection.

    Modes:
    - 'docker':     Always use Docker containers (fails if Docker unavailable)
    - 'subprocess': Always use subprocess (less secure, no Docker needed)
    - 'auto':       Use Docker if available, fall back to subprocess
    """

    def __init__(self):
        self._docker = DockerExecutor()
        self._subprocess = SubprocessExecutor()
        self._mode = settings.sandbox.mode

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Executes code in the selected sandbox environment."""
        if self._mode == "docker":
            log.info("Executing in Docker sandbox (language={})", request.language)
            return self._docker.execute(request)

        elif self._mode == "subprocess":
            log.info("Executing in subprocess sandbox (language={})", request.language)
            return self._subprocess.execute(request)

        else:  # auto
            if self._docker.is_available:
                log.info("Auto-selected Docker sandbox (language={})", request.language)
                return self._docker.execute(request)
            else:
                log.info(
                    "Docker unavailable — using subprocess fallback (language={})",
                    request.language,
                )
                return self._subprocess.execute(request)

    @property
    def is_docker_available(self) -> bool:
        """Returns whether Docker is available for execution."""
        return self._docker.is_available

    @property
    def active_mode(self) -> str:
        """Returns the currently active execution mode."""
        if self._mode == "auto":
            return "docker" if self._docker.is_available else "subprocess"
        return self._mode
