"""
FacultyIQ Video Evidence Extraction Service — API Dependencies.

FastAPI dependency injection providers for pipeline services.
"""

from app.services.pipeline_orchestrator import PipelineOrchestrator

_orchestrator_instance: PipelineOrchestrator | None = None


def get_orchestrator() -> PipelineOrchestrator:
    """Dependency provider returning singleton PipelineOrchestrator instance."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = PipelineOrchestrator()
    return _orchestrator_instance
