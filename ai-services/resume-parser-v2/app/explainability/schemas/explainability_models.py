"""
Canonical Pydantic v2 Models for Enterprise Explainability, Audit & Evidence Intelligence Engine.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app.recruitment_agent.schemas.decision_models import RecruitmentDecisionReport


class ExplainabilityRequest(BaseModel):
    decision_report: RecruitmentDecisionReport
    initiator_id: str = Field(default="system_user")


class ExplanationItem(BaseModel):
    metric_name: str
    score_or_value: str
    explanation_text: str
    supporting_evidence: List[str] = Field(default_factory=list)


class AuditRecord(BaseModel):
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    candidate_name: str
    initiator_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    config_hash: str = "v2.0.0-sha256"
    prompt_version: str = "v1.0"
    llm_model: str = "llama3.2"
    rag_sources_count: int = 3
    evidence_citation_ids: List[str] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    stage_number: int
    stage_name: str
    status: str = "COMPLETED"
    details: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceReport(BaseModel):
    is_compliant: bool = True
    evidence_completeness_pct: float = 100.0
    policy_violations: List[str] = Field(default_factory=list)
    unbacked_claims: List[str] = Field(default_factory=list)


class VersionInfo(BaseModel):
    system_version: str = "2.0.0"
    pipeline_build: str = "FacultyIQ-V2-Production"
    python_version: str = "3.12"


class ExplainabilityReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    document_uuid: str
    candidate_name: str
    position_title: str
    decision_summary: Dict[str, Any] = Field(default_factory=dict)
    explanations: List[ExplanationItem] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    audit: AuditRecord = Field(default_factory=lambda: AuditRecord(decision_id="tmp", candidate_name="tmp", initiator_id="tmp"))
    timeline: List[TimelineEvent] = Field(default_factory=list)
    compliance: ComplianceReport = Field(default_factory=ComplianceReport)
    versioning: VersionInfo = Field(default_factory=VersionInfo)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
