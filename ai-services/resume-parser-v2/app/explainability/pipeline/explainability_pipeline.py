"""
End-to-End Enterprise Explainability, Audit & Evidence Pipeline.
Orchestrates Audit Record creation, Stage Timeline Chronology, Score Explanations, Compliance Validation, and Audit Repository persistence.
"""

import time
from app.explainability.audit.audit_engine import AuditEngine
from app.explainability.compliance.compliance_validator import ComplianceValidatorEngine
from app.explainability.reports.report_generator import ReportGeneratorEngine
from app.explainability.schemas.explainability_models import ExplainabilityReport, ExplainabilityRequest, VersionInfo
from app.explainability.services.audit_service import AuditRepositoryService
from app.explainability.timeline.timeline_builder import TimelineBuilderEngine
from app.explainability.traceability.traceability_engine import TraceabilityEngine
from core.logging import get_logger

logger = get_logger("explainability_pipeline")


class ExplainabilityPipeline:
    """Enterprise Governance & Explainability Pipeline Engine."""

    def __init__(self) -> None:
        self.audit_engine = AuditEngine()
        self.timeline_builder = TimelineBuilderEngine()
        self.traceability_engine = TraceabilityEngine()
        self.compliance_validator = ComplianceValidatorEngine()
        self.report_generator = ReportGeneratorEngine()
        self.audit_service = AuditRepositoryService.get_instance()

    async def generate_explainability_report(
        self, request: ExplainabilityRequest
    ) -> ExplainabilityReport:
        """Executes full explainability & audit pipeline."""
        start_time = time.perf_counter()
        decision = request.decision_report

        # Step 1: Create Audit Record
        audit_record = self.audit_engine.create_audit_record(decision, request.initiator_id)

        # Step 2: Build Pipeline Stage Timeline Chronology
        timeline = self.timeline_builder.build_pipeline_timeline()

        # Step 3: Build Explanations & Evidence Citations
        explanations = self.traceability_engine.build_explanations(decision)

        # Step 4: Validate Legal & Policy Compliance
        compliance = self.compliance_validator.validate_compliance(decision)

        # Step 5: Build Decision Summary
        summary_dict = self.report_generator.build_decision_summary(decision)

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        report = ExplainabilityReport(
            decision_id=decision.decision_id,
            document_uuid=decision.document_uuid,
            candidate_name=decision.candidate_name,
            position_title=decision.position_title,
            decision_summary=summary_dict,
            explanations=explanations,
            evidence=decision.evidence,
            audit=audit_record,
            timeline=timeline,
            compliance=compliance,
            versioning=VersionInfo(),
            processing_time_ms=processing_time_ms,
        )

        # Save to Repository
        self.audit_service.save_report(report)

        logger.info(
            "Explainability pipeline complete",
            report_id=report.report_id,
            decision_id=decision.decision_id,
            candidate=decision.candidate_name,
            duration_ms=processing_time_ms,
        )

        return report
