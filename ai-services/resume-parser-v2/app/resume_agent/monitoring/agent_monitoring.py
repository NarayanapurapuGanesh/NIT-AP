"""
Agent Monitoring Engine.
Logs performance metrics, latency, token consumption, and model selection.
"""

from app.resume_agent.schemas.agent_models import TokenMetrics
from core.logging import get_logger

logger = get_logger("agent_monitoring")


class AgentMonitoringEngine:
    """Agent Telemetry & Token Monitor Engine."""

    def log_execution(self, doc_uuid: str, metrics: TokenMetrics) -> None:
        logger.info(
            "Resume Intelligence Agent execution complete",
            doc_uuid=doc_uuid,
            model=metrics.model_name,
            total_tokens=metrics.total_tokens,
            latency_ms=metrics.latency_ms,
        )
