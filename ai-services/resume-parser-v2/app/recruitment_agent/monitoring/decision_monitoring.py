"""
Decision Telemetry & Monitoring Engine.
Logs multi-agent decision metrics, consensus outcomes, and execution latency.
"""

from core.logging import get_logger

logger = get_logger("decision_monitoring")


class DecisionMonitoringEngine:
    """Decision Telemetry Monitor."""

    def log_decision_metrics(
        self, candidate_name: str, recommendation: str, latency_ms: float
    ) -> None:
        logger.info(
            "Recruitment decision multi-agent consensus complete",
            candidate=candidate_name,
            recommendation=recommendation,
            latency_ms=latency_ms,
        )
