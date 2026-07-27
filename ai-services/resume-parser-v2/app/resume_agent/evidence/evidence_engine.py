"""
Evidence Engine.
Attaches evidence citations to reasoning outputs based on Phase 5 report data.
"""

from typing import List
from app.resume_agent.schemas.agent_models import EvidenceCitation
from app.resume_intelligence.schemas.intelligence_report import CandidateIntelligenceReport
from core.logging import get_logger

logger = get_logger("evidence_engine")


class EvidenceEngine:
    """Evidence Citation Attacher."""

    def build_citations(self, report: CandidateIntelligenceReport) -> List[EvidenceCitation]:
        citations: List[EvidenceCitation] = []

        citations.append(
            EvidenceCitation(
                citation_id="cite_001",
                source_field="candidate_name",
                extracted_value=report.candidate_name,
                confidence=1.0,
            )
        )

        if report.research.publication_count > 0:
            citations.append(
                EvidenceCitation(
                    citation_id="cite_002",
                    source_field="research.publication_count",
                    extracted_value=str(report.research.publication_count),
                    confidence=1.0,
                )
            )

        return citations
