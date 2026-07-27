"""
Structured Logging Engine.
Provides JSON structured log formatting, correlation via trace IDs, and categorized log channels.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from core.logging import get_logger

logger = get_logger("logging_engine")


class StructuredLoggingEngine:
    """Enterprise Structured Logging Engine."""

    def __init__(self) -> None:
        self._log_buffer: List[Dict[str, Any]] = []

    def log(
        self,
        level: str,
        message: str,
        category: str = "application",
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        **extra: Any,
    ) -> Dict[str, Any]:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.upper(),
            "category": category,
            "message": message,
            "trace_id": trace_id,
            "correlation_id": correlation_id,
            **extra,
        }
        self._log_buffer.append(entry)

        if level.upper() == "ERROR":
            logger.error(message, category=category, trace_id=trace_id, **extra)
        elif level.upper() == "WARNING":
            logger.warning(message, category=category, trace_id=trace_id, **extra)
        else:
            logger.info(message, category=category, trace_id=trace_id, **extra)

        return entry

    def log_security(self, message: str, **extra: Any) -> Dict[str, Any]:
        return self.log("WARNING", message, category="security", **extra)

    def log_ai(self, message: str, **extra: Any) -> Dict[str, Any]:
        return self.log("INFO", message, category="ai", **extra)

    def log_workflow(self, message: str, **extra: Any) -> Dict[str, Any]:
        return self.log("INFO", message, category="workflow", **extra)

    def log_audit(self, message: str, **extra: Any) -> Dict[str, Any]:
        return self.log("INFO", message, category="audit", **extra)

    def get_recent_logs(self, limit: int = 100, category: Optional[str] = None) -> List[Dict[str, Any]]:
        logs = self._log_buffer
        if category:
            logs = [l for l in logs if l.get("category") == category]
        return logs[-limit:]

    def export_json_lines(self, limit: int = 100) -> str:
        logs = self._log_buffer[-limit:]
        return "\n".join(json.dumps(entry) for entry in logs)
