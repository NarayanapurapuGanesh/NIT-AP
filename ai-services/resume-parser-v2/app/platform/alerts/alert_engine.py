"""
Alert Engine.
Configurable alert rules for high latency, service failures, AI failures, queue backlog,
disk/memory pressure. Evaluates rules against live metrics and fires alert events.
"""

from typing import Dict, List
from app.platform.schemas.platform_models import AlertEvent, AlertRule, AlertSeverity
from core.logging import get_logger

logger = get_logger("alert_engine")


class AlertEngine:
    """Enterprise Alert Management Engine."""

    def __init__(self) -> None:
        self._rules: Dict[str, AlertRule] = {}
        self._alert_history: List[AlertEvent] = []
        self._seed_default_rules()

    def _seed_default_rules(self) -> None:
        defaults = [
            ("High API Latency", "facultyiq_api_latency_avg_ms", "gt", 250.0, AlertSeverity.WARNING),
            ("Critical API Latency", "facultyiq_api_latency_avg_ms", "gt", 500.0, AlertSeverity.CRITICAL),
            ("AI Inference Slow", "facultyiq_ai_inference_latency_avg_ms", "gt", 5000.0, AlertSeverity.WARNING),
            ("Queue Backlog", "facultyiq_queue_length", "gt", 50.0, AlertSeverity.WARNING),
            ("High Memory Usage", "facultyiq_memory_usage_percent", "gt", 90.0, AlertSeverity.CRITICAL),
            ("High CPU Usage", "facultyiq_cpu_usage_percent", "gt", 85.0, AlertSeverity.WARNING),
        ]
        for name, metric, cond, threshold, severity in defaults:
            rule = AlertRule(name=name, metric_name=metric, condition=cond, threshold=threshold, severity=severity)
            self._rules[rule.rule_id] = rule

        logger.info("Seeded default alert rules", count=len(self._rules))

    def evaluate_rules(self, metrics: Dict[str, float]) -> List[AlertEvent]:
        """Evaluate all active rules against current metric values."""
        fired: List[AlertEvent] = []

        for rule in self._rules.values():
            if not rule.is_active:
                continue

            current = metrics.get(rule.metric_name)
            if current is None:
                continue

            triggered = False
            if rule.condition == "gt" and current > rule.threshold:
                triggered = True
            elif rule.condition == "lt" and current < rule.threshold:
                triggered = True
            elif rule.condition == "eq" and current == rule.threshold:
                triggered = True

            if triggered:
                event = AlertEvent(
                    rule_id=rule.rule_id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    current_value=current,
                    threshold=rule.threshold,
                    message=f"Alert: {rule.name} - current value {current} {rule.condition} threshold {rule.threshold}",
                )
                fired.append(event)
                self._alert_history.append(event)
                logger.warning("Alert fired", rule_name=rule.name, current=current, threshold=rule.threshold)

        return fired

    def get_alert_history(self, limit: int = 50) -> List[AlertEvent]:
        return self._alert_history[-limit:]

    def list_rules(self) -> List[AlertRule]:
        return list(self._rules.values())
