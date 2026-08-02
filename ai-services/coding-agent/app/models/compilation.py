"""
FacultyIQ Coding Intelligence Agent — Compilation Models.
"""

from typing import Optional, List
from pydantic import BaseModel


class CompilationResult(BaseModel):
    success: bool = False
    error_message: str = ""
    warnings: List[str] = []
    compilation_time_ms: float = 0.0


class RuntimeMetrics(BaseModel):
    execution_time_ms: float = 0.0
    memory_used_kb: float = 0.0
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
