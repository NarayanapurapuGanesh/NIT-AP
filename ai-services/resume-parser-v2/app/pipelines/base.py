"""
Base contracts and state abstractions for the Modular Pipeline Framework.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class PipelineContext:
    """Shared state container passed sequentially through pipeline steps."""

    document_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_error(self, step_name: str, error: str) -> None:
        self.errors.append({"step": step_name, "error": error, "timestamp": datetime.now(timezone.utc).isoformat()})

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


@dataclass
class PipelineResult:
    """Execution output summary of a pipeline run."""

    pipeline_name: str
    success: bool
    context: PipelineContext
    execution_time_ms: float
    completed_steps: List[str]


class IPipelineStep(ABC):
    """Abstract interface representing a single step within a pipeline."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the step."""
        pass

    @abstractmethod
    async def execute(self, context: PipelineContext) -> PipelineContext:
        """Processes and transforms the pipeline context state."""
        pass
