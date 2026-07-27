"""
Pipeline Registration Framework & Step Orchestrator.
Allows modular registration and execution of dynamic analysis pipelines.
"""

import time
from typing import Dict, List
from core.exceptions import PipelineExecutionError, PipelineNotFoundError
from core.logging import get_logger
from app.pipelines.base import IPipelineStep, PipelineContext, PipelineResult

logger = get_logger("pipeline_registry")


class Pipeline:
    """Sequential sequence of pipeline steps."""

    def __init__(self, name: str, steps: List[IPipelineStep]) -> None:
        self.name = name
        self.steps = steps

    async def run(self, context: PipelineContext) -> PipelineResult:
        """Runs all registered steps sequentially through the given context."""
        start_time = time.perf_counter()
        completed_steps: List[str] = []

        logger.info("Starting pipeline execution", pipeline_name=self.name, document_id=context.document_id)

        for step in self.steps:
            step_name = step.name
            logger.debug("Executing pipeline step", pipeline_name=self.name, step=step_name)
            try:
                context = await step.execute(context)
                completed_steps.append(step_name)
                if not context.is_valid:
                    logger.warning("Pipeline context error detected", step=step_name, errors=context.errors)
            except Exception as exc:
                logger.error("Pipeline step failed with exception", step=step_name, error=str(exc))
                context.add_error(step_name, str(exc))
                raise PipelineExecutionError(step_name=step_name, reason=str(exc)) from exc

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            "Completed pipeline execution",
            pipeline_name=self.name,
            duration_ms=execution_time_ms,
            steps_completed=len(completed_steps),
        )

        return PipelineResult(
            pipeline_name=self.name,
            success=context.is_valid,
            context=context,
            execution_time_ms=execution_time_ms,
            completed_steps=completed_steps,
        )


class PipelineRegistry:
    """Central container for registering and retrieving pipelines."""

    def __init__(self) -> None:
        self._pipelines: Dict[str, Pipeline] = {}

    def register(self, name: str, steps: List[IPipelineStep]) -> None:
        """Registers a named pipeline composed of the provided steps."""
        if name in self._pipelines:
            logger.warning("Overwriting existing pipeline registration", pipeline_name=name)
        self._pipelines[name] = Pipeline(name=name, steps=steps)
        logger.info("Pipeline registered successfully", pipeline_name=name, step_count=len(steps))

    def get(self, name: str) -> Pipeline:
        """Retrieves a registered pipeline by name."""
        if name not in self._pipelines:
            raise PipelineNotFoundError(name)
        return self._pipelines[name]

    def list_pipelines(self) -> List[str]:
        """Lists all registered pipeline names."""
        return list(self._pipelines.keys())


# Global Singleton Pipeline Registry Instance
pipeline_registry = PipelineRegistry()
