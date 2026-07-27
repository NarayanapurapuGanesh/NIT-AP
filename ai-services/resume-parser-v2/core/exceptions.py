"""
Custom exception hierarchy for resume-parser-v2.
Provides clean error handling, standard error payloads, and typed exceptions.
"""

from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """Base exception class for all custom application errors."""

    def __init__(
        self,
        message: str = "An unexpected application error occurred.",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ConfigurationError(BaseAppException):
    """Raised when environment or startup configuration is invalid."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=500, details=details)


class ServiceNotFoundError(BaseAppException):
    """Raised when a requested service is not registered in the ServiceRegistry."""

    def __init__(self, service_name: str) -> None:
        message = f"Service '{service_name}' was not found in the service registry."
        super().__init__(message=message, status_code=404, details={"service_name": service_name})


class PipelineNotFoundError(BaseAppException):
    """Raised when a requested pipeline is not registered in the PipelineRegistry."""

    def __init__(self, pipeline_name: str) -> None:
        message = f"Pipeline '{pipeline_name}' was not found in the pipeline registry."
        super().__init__(message=message, status_code=404, details={"pipeline_name": pipeline_name})


class PipelineExecutionError(BaseAppException):
    """Raised when an error occurs during execution of a pipeline step."""

    def __init__(self, step_name: str, reason: str) -> None:
        message = f"Pipeline execution failed at step '{step_name}': {reason}"
        super().__init__(
            message=message,
            status_code=500,
            details={"step_name": step_name, "reason": reason},
        )


class ValidationException(BaseAppException):
    """Raised when input validation fails across pipeline schemas or inputs."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=422, details=details)
