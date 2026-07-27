"""
Audit Repository Storage Service.
In-memory and persistent repository for saving and retrieving AuditRecords and ExplainabilityReports.
"""

from typing import Dict, List, Optional
from app.explainability.schemas.explainability_models import AuditRecord, ExplainabilityReport
from core.logging import get_logger

logger = get_logger("audit_service")


class AuditRepositoryService:
    """Audit & Evidence Repository Service."""

    _instance: Optional["AuditRepositoryService"] = None

    def __init__(self) -> None:
        self._reports_by_decision: Dict[str, ExplainabilityReport] = {}
        self._audits_by_decision: Dict[str, AuditRecord] = {}

    @classmethod
    def get_instance(cls) -> "AuditRepositoryService":
        if cls._instance is None:
            cls._instance = AuditRepositoryService()
        return cls._instance

    def save_report(self, report: ExplainabilityReport) -> None:
        self._reports_by_decision[report.decision_id] = report
        self._audits_by_decision[report.decision_id] = report.audit
        logger.info("Saved explainability report to repository", decision_id=report.decision_id)

    def get_audit_record(self, decision_id: str) -> Optional[AuditRecord]:
        return self._audits_by_decision.get(decision_id)

    def get_report(self, decision_id: str) -> Optional[ExplainabilityReport]:
        return self._reports_by_decision.get(decision_id)
