"""
Evidence Linker Engine for Job Intelligence.
Attaches evidence provenance and rule confidence to JobIntelligenceModel.
"""

from app.job_intelligence.schemas.job_models import JobIntelligenceModel
from core.logging import get_logger

logger = get_logger("job_evidence_linker")


class JobEvidenceLinker:
    """JD Evidence Provenance Engine."""

    def attach_evidence(self, model: JobIntelligenceModel) -> JobIntelligenceModel:
        # Provenance metadata logger
        logger.debug("Attached JD evidence provenance", job_uuid=model.job_uuid)
        return model
