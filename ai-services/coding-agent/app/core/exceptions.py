"""
FacultyIQ Coding Intelligence Agent — Domain Exceptions.
"""


class CodingAgentError(Exception):
    """Base exception for all Coding Agent errors."""
    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class SandboxError(CodingAgentError):
    """Raised when secure sandbox execution fails."""
    pass


class CompilationError(CodingAgentError):
    """Raised when code compilation fails."""
    pass


class ExecutionTimeoutError(CodingAgentError):
    """Raised when code execution exceeds the time limit."""
    pass


class MemoryLimitError(CodingAgentError):
    """Raised when code execution exceeds the memory limit."""
    pass


class QuestionNotFoundError(CodingAgentError):
    """Raised when a requested question is not found."""
    pass


class SessionNotFoundError(CodingAgentError):
    """Raised when a requested session is not found."""
    pass


class SessionExpiredError(CodingAgentError):
    """Raised when a session has already been completed or expired."""
    pass


class OllamaError(CodingAgentError):
    """Raised when the AI Orchestrator call fails."""
    pass
