"""
FacultyIQ Coding Intelligence Agent — Docker Executor.

Secure code execution using Docker containers with resource limits,
network isolation, and read-only filesystem.
"""

import time
from typing import Optional

from app.config.settings import settings
from app.core.logging import get_module_logger
from app.models.sandbox import ExecutionRequest, ExecutionResult, ExecutionStatus

log = get_module_logger("sandbox")

# Docker image names for each language
DOCKER_IMAGES = {
    "python": "facultyiq-sandbox-python:latest",
    "c": "facultyiq-sandbox-cpp:latest",
    "cpp": "facultyiq-sandbox-cpp:latest",
    "java": "facultyiq-sandbox-java:latest",
    "javascript": "facultyiq-sandbox-javascript:latest",
    "csharp": "facultyiq-sandbox-csharp:latest",
}


class DockerExecutor:
    """Executes code inside secure Docker containers."""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Lazy-loads the Docker client."""
        if self._client is None:
            try:
                import docker
                self._client = docker.from_env()
                self._client.ping()
                log.info("Docker client connected successfully.")
            except Exception as exc:
                log.warning("Docker not available: {}", exc)
                self._client = None
        return self._client

    @property
    def is_available(self) -> bool:
        """Checks if Docker daemon is reachable."""
        try:
            return self.client is not None
        except Exception:
            return False

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Runs code in a Docker container with full isolation."""
        if not self.is_available:
            return ExecutionResult(
                status=ExecutionStatus.SANDBOX_ERROR,
                stderr="Docker daemon not available",
            )

        image = DOCKER_IMAGES.get(request.language)
        if not image:
            return ExecutionResult(
                status=ExecutionStatus.SANDBOX_ERROR,
                stderr=f"No Docker image for language: {request.language}",
            )

        start_time = time.perf_counter()
        container = None

        try:
            # Build the execution command
            code_escaped = request.source_code.replace("'", "'\\''")
            stdin_escaped = request.stdin.replace("'", "'\\''")

            if request.language == "python":
                cmd = f"echo '{code_escaped}' > /tmp/sol.py && echo '{stdin_escaped}' | python3 /tmp/sol.py"
            elif request.language in ("c", "cpp"):
                compiler = "gcc" if request.language == "c" else "g++"
                ext = ".c" if request.language == "c" else ".cpp"
                flags = "-lm" if request.language == "c" else "-std=c++17"
                cmd = f"echo '{code_escaped}' > /tmp/sol{ext} && {compiler} /tmp/sol{ext} -o /tmp/sol {flags} && echo '{stdin_escaped}' | /tmp/sol"
            elif request.language == "java":
                cmd = f"echo '{code_escaped}' > /tmp/Solution.java && javac /tmp/Solution.java && echo '{stdin_escaped}' | java -cp /tmp Solution"
            elif request.language == "javascript":
                cmd = f"echo '{code_escaped}' > /tmp/sol.js && echo '{stdin_escaped}' | node /tmp/sol.js"
            elif request.language == "csharp":
                cmd = f"echo '{code_escaped}' > /tmp/sol.cs && csc /tmp/sol.cs /out:/tmp/sol.exe && echo '{stdin_escaped}' | mono /tmp/sol.exe"
            else:
                return ExecutionResult(
                    status=ExecutionStatus.SANDBOX_ERROR,
                    stderr=f"Unsupported language: {request.language}",
                )

            # Run container with security constraints
            container = self.client.containers.run(
                image=image,
                command=["sh", "-c", cmd],
                detach=True,
                mem_limit=f"{request.memory_limit_mb}m",
                cpu_period=100000,
                cpu_quota=int(settings.sandbox.cpu_limit * 100000),
                network_disabled=True,
                read_only=False,      # /tmp needs to be writable
                pids_limit=64,
                security_opt=["no-new-privileges"],
                tmpfs={"/tmp": "size=50m"},
            )

            # Wait for completion with timeout
            result = container.wait(timeout=request.timeout_seconds)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
            stdout_logs = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
            stderr_logs = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")

            exit_code = result.get("StatusCode", -1)

            if exit_code != 0:
                # Check if it's a compilation error vs runtime error
                if "error:" in stderr_logs.lower() and elapsed_ms < 2000:
                    return ExecutionResult(
                        status=ExecutionStatus.COMPILATION_ERROR,
                        stdout=stdout_logs[:settings.sandbox.max_output_bytes],
                        stderr=stderr_logs[:settings.sandbox.max_output_bytes],
                        exit_code=exit_code,
                        execution_time_ms=round(elapsed_ms, 2),
                        compiled_ok=False,
                        compilation_error=stderr_logs[:settings.sandbox.max_output_bytes],
                    )

                return ExecutionResult(
                    status=ExecutionStatus.RUNTIME_ERROR,
                    stdout=stdout_logs[:settings.sandbox.max_output_bytes],
                    stderr=stderr_logs[:settings.sandbox.max_output_bytes],
                    exit_code=exit_code,
                    execution_time_ms=round(elapsed_ms, 2),
                )

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                stdout=stdout_logs[:settings.sandbox.max_output_bytes],
                stderr=stderr_logs[:settings.sandbox.max_output_bytes],
                exit_code=0,
                execution_time_ms=round(elapsed_ms, 2),
            )

        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            error_msg = str(exc)

            if "timeout" in error_msg.lower() or "read timed out" in error_msg.lower():
                return ExecutionResult(
                    status=ExecutionStatus.TIMEOUT,
                    stderr=f"Time Limit Exceeded ({request.timeout_seconds}s)",
                    execution_time_ms=round(elapsed_ms, 2),
                )

            if "oom" in error_msg.lower():
                return ExecutionResult(
                    status=ExecutionStatus.MEMORY_LIMIT,
                    stderr=f"Memory Limit Exceeded ({request.memory_limit_mb}MB)",
                    execution_time_ms=round(elapsed_ms, 2),
                )

            log.error("Docker execution error: {}", exc)
            return ExecutionResult(
                status=ExecutionStatus.SANDBOX_ERROR,
                stderr=error_msg,
                execution_time_ms=round(elapsed_ms, 2),
            )

        finally:
            # Cleanup container
            if container and settings.sandbox.cleanup_containers:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
