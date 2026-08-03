"""
FacultyIQ Coding Intelligence Agent — Subprocess Executor.

Fallback code execution engine using subprocess with timeout enforcement.
Used when Docker is not available.
"""

import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional

from app.config.settings import settings
from app.core.logging import get_module_logger
from app.models.sandbox import ExecutionRequest, ExecutionResult, ExecutionStatus

log = get_module_logger("sandbox")

# Language-specific compilation and execution commands
LANGUAGE_CONFIG = {
    "python": {
        "extension": ".py",
        "compile_cmd": None,
        "run_cmd": lambda f: ["python", str(f)],
    },
    "c": {
        "extension": ".c",
        "compile_cmd": lambda f, o: ["gcc", str(f), "-o", str(o), "-lm"],
        "run_cmd": lambda f: [str(f)],
    },
    "cpp": {
        "extension": ".cpp",
        "compile_cmd": lambda f, o: ["g++", str(f), "-o", str(o), "-std=c++17"],
        "run_cmd": lambda f: [str(f)],
    },
    "java": {
        "extension": ".java",
        "compile_cmd": lambda f, o: ["javac", str(f)],
        "run_cmd": lambda f: ["java", "-cp", str(f.parent), f.stem],
    },
    "javascript": {
        "extension": ".js",
        "compile_cmd": None,
        "run_cmd": lambda f: ["node", str(f)],
    },
    "csharp": {
        "extension": ".cs",
        "compile_cmd": lambda f, o: ["csc", f"/out:{o}", str(f)],
        "run_cmd": lambda f: [str(f)],
    },
}


class SubprocessExecutor:
    """Executes code in a subprocess with timeout and resource limits."""

    def __init__(self):
        self.temp_base = settings.base_dir / settings.storage.temp_dir / "sandbox"
        self.temp_base.mkdir(parents=True, exist_ok=True)

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Compiles (if needed) and runs code in a subprocess."""
        lang_config = LANGUAGE_CONFIG.get(request.language)
        if not lang_config:
            return ExecutionResult(
                status=ExecutionStatus.SANDBOX_ERROR,
                stderr=f"Unsupported language: {request.language}",
            )

        # Create temp directory for this execution
        work_dir = Path(tempfile.mkdtemp(dir=str(self.temp_base)))

        try:
            # Write source code to file
            source_file = work_dir / f"solution{lang_config['extension']}"

            # For Java, the class name must match the filename
            if request.language == "java":
                # Extract class name from source code
                import re
                match = re.search(r'public\s+class\s+(\w+)', request.source_code)
                class_name = match.group(1) if match else "Solution"
                source_file = work_dir / f"{class_name}.java"

            source_file.write_text(request.source_code, encoding="utf-8")

            # Compile if needed
            if lang_config["compile_cmd"]:
                compiled = self._compile(
                    source_file, work_dir, lang_config, request.timeout_seconds
                )
                if compiled.status != ExecutionStatus.SUCCESS:
                    return compiled

            # Execute
            return self._run(
                source_file, work_dir, lang_config, request
            )

        except Exception as exc:
            log.error("Subprocess execution error: {}", exc)
            return ExecutionResult(
                status=ExecutionStatus.SANDBOX_ERROR,
                stderr=str(exc),
            )
        finally:
            # Cleanup
            try:
                import shutil
                shutil.rmtree(work_dir, ignore_errors=True)
            except Exception:
                pass

    def _compile(
        self,
        source_file: Path,
        work_dir: Path,
        lang_config: dict,
        timeout: int,
    ) -> ExecutionResult:
        """Compiles source code and returns result."""
        if source_file.suffix == ".java":
            compile_cmd = lang_config["compile_cmd"](source_file, None)
        else:
            output_file = work_dir / "solution"
            if os.name == "nt":
                output_file = work_dir / "solution.exe"
            compile_cmd = lang_config["compile_cmd"](source_file, output_file)

        log.debug("Compiling: {}", " ".join(compile_cmd))

        try:
            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(work_dir),
            )
        except FileNotFoundError as e:
            return ExecutionResult(
                status=ExecutionStatus.SANDBOX_ERROR,
                stderr=f"Compiler not found. Please ensure {compile_cmd[0]} is installed and in PATH.\n[WinError 2] The system cannot find the file specified",
                compiled_ok=False,
            )

            if result.returncode != 0:
                return ExecutionResult(
                    status=ExecutionStatus.COMPILATION_ERROR,
                    stderr=result.stderr,
                    exit_code=result.returncode,
                    compiled_ok=False,
                    compilation_error=result.stderr,
                )

            return ExecutionResult(status=ExecutionStatus.SUCCESS, compiled_ok=True)

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                stderr="Compilation timed out",
                compiled_ok=False,
            )

    def _run(
        self,
        source_file: Path,
        work_dir: Path,
        lang_config: dict,
        request: ExecutionRequest,
    ) -> ExecutionResult:
        """Runs the compiled/interpreted code."""
        if request.language in ("c", "cpp", "csharp"):
            exe = work_dir / ("solution.exe" if os.name == "nt" else "solution")
            run_cmd = lang_config["run_cmd"](exe)
        else:
            run_cmd = lang_config["run_cmd"](source_file)

        log.debug("Running: {}", " ".join(str(c) for c in run_cmd))

        start_time = time.perf_counter()

        try:
            result = subprocess.run(
                run_cmd,
                input=request.stdin,
                capture_output=True,
                text=True,
                timeout=request.timeout_seconds,
                cwd=str(work_dir),
            )
        except FileNotFoundError as e:
            return ExecutionResult(
                status=ExecutionStatus.SANDBOX_ERROR,
                stderr=f"Runtime not found. Please ensure {run_cmd[0]} is installed and in PATH.\n[WinError 2] The system cannot find the file specified",
                exit_code=-1,
                execution_time_ms=0,
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000

            if result.returncode != 0:
                return ExecutionResult(
                    status=ExecutionStatus.RUNTIME_ERROR,
                    stdout=result.stdout[:settings.sandbox.max_output_bytes],
                    stderr=result.stderr[:settings.sandbox.max_output_bytes],
                    exit_code=result.returncode,
                    execution_time_ms=round(elapsed_ms, 2),
                )

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                stdout=result.stdout[:settings.sandbox.max_output_bytes],
                stderr=result.stderr[:settings.sandbox.max_output_bytes],
                exit_code=0,
                execution_time_ms=round(elapsed_ms, 2),
            )

        except subprocess.TimeoutExpired:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                stderr=f"Time Limit Exceeded ({request.timeout_seconds}s)",
                execution_time_ms=round(elapsed_ms, 2),
            )
