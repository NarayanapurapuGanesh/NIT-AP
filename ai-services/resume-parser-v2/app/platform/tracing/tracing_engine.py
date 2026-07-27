"""
OpenTelemetry-Compatible Distributed Tracing Engine.
Provides span creation, correlation ID propagation, and request/AI/workflow tracing.
"""

import time
import uuid
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional
from app.platform.schemas.platform_models import TraceSpan
from core.logging import get_logger

logger = get_logger("tracing_engine")


class TracingEngine:
    """Enterprise Distributed Tracing Engine."""

    def __init__(self) -> None:
        self._active_spans: Dict[str, TraceSpan] = {}
        self._completed_spans: List[TraceSpan] = []

    def generate_trace_id(self) -> str:
        return str(uuid.uuid4())

    def generate_correlation_id(self) -> str:
        return f"corr-{uuid.uuid4().hex[:16]}"

    def create_span(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> TraceSpan:
        span = TraceSpan(
            trace_id=trace_id or self.generate_trace_id(),
            operation_name=operation_name,
            parent_span_id=parent_span_id,
            attributes=attributes or {},
        )
        self._active_spans[span.span_id] = span
        return span

    def end_span(self, span: TraceSpan, status: str = "ok") -> TraceSpan:
        duration = (time.time() - span.start_time.timestamp()) * 1000
        span.duration_ms = round(duration, 2)
        span.status = status
        self._active_spans.pop(span.span_id, None)
        self._completed_spans.append(span)
        logger.debug(
            "Span completed",
            trace_id=span.trace_id,
            span_id=span.span_id,
            operation=span.operation_name,
            duration_ms=span.duration_ms,
        )
        return span

    @contextmanager
    def trace(
        self,
        operation_name: str,
        trace_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Generator[TraceSpan, None, None]:
        """Context manager for automatic span lifecycle."""
        span = self.create_span(operation_name, trace_id=trace_id, attributes=attributes)
        try:
            yield span
            self.end_span(span, status="ok")
        except Exception as e:
            span.attributes["error"] = str(e)
            self.end_span(span, status="error")
            raise

    def get_recent_spans(self, limit: int = 50) -> List[TraceSpan]:
        return self._completed_spans[-limit:]
