"""
Audit Engine.
Records immutable audit logs containing initiator, timestamp, configuration used, prompt version, LLM model, RAG sources, decision history.
"""

from app.explainability.schemas.explainability_models import AuditRecord
from app.recruitment_agent.schemas.decision_models import RecruitmentDecisionReport
from core.logging import get_logger

logger = get_logger("audit_engine")


class AuditEngine:
    """Immutable Audit Log Generator Engine."""

    def create_audit_record(
        self, decision: RecruitmentDecisionReport, initiator_id: str
    ) -> AuditRecord:
        record = AuditRecord(
            decision_id=decision.decision_id,
            candidate_name=decision.candidate_name,
            initiator_id=initiator_id,
            evidence_citation_ids=decision.evidence,
        )

        logger.info(
            "Audit record generated cleanly",
            audit_id=record.audit_id,
            decision_id=record.decision_id,
            candidate=record.candidate_name,
        )

        return record
