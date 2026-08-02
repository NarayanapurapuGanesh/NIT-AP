"""
FacultyIQ Coding Intelligence Agent — Sandbox Pydantic Models.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    COMPILATION_ERROR = "compilation_error"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    MEMORY_LIMIT = "memory_limit"
    SANDBOX_ERROR = "sandbox_error"


class ExecutionRequest(BaseModel):
    source_code: str
    language: str
    stdin: str = ""
    timeout_seconds: int = 15
    memory_limit_mb: int = 256


class ExecutionResult(BaseModel):
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
    execution_time_ms: float = 0.0
    memory_used_kb: float = 0.0
    compiled_ok: bool = True
    compilation_error: str = ""
