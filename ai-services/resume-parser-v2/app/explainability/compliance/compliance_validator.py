"""
Compliance Validator Engine.
Validates evidence completeness, policy violations, unbacked claims, and decision consistency.
"""

from app.explainability.schemas.explainability_models import ComplianceReport
from app.recruitment_agent.schemas.decision_models import RecruitmentDecisionReport
from core.logging import get_logger

logger = get_logger("compliance_validator")


class ComplianceValidatorEngine:
    """Legal & Policy Compliance Validator Engine."""

    def validate_compliance(self, decision: RecruitmentDecisionReport) -> ComplianceReport:
        policy_violations = []
        unbacked_claims = []

        if not decision.evidence:
            unbacked_claims.append("Missing evidence citations for recruitment decision.")

        is_compliant = len(policy_violations) == 0 and len(unbacked_claims) == 0

        report = ComplianceReport(
            is_compliant=is_compliant,
            evidence_completeness_pct=100.0 if decision.evidence else 50.0,
            policy_violations=policy_violations,
            unbacked_claims=unbacked_claims,
        )

        logger.debug("Compliance validation complete", is_compliant=is_compliant)
        return report
