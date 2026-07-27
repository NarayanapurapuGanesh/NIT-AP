"""
Layer 9: Classification Result Builder.
Constructs the final structured ClassificationResult output payload.
"""

from typing import Any, Dict, List
from classifiers.engine.metadata_extractor import DocumentMetadata
from schemas.classification import ClassificationResult, EvidenceItem, NextStageEnum
from core.logging import get_logger

logger = get_logger("result_builder")


class ClassificationResultBuilder:
    """Layer 9: Classification Result Builder."""

    def build_result(
        self,
        document_type: str,
        confidence: float,
        accepted_types: List[str],
        reasons: List[str],
        evidence: List[EvidenceItem],
        metadata: DocumentMetadata,
        processing_time_ms: float,
    ) -> ClassificationResult:
        accepted = document_type in accepted_types

        if accepted:
            next_stage = NextStageEnum.TEXT_EXTRACTION.value
        elif document_type in ["Invoice", "Marksheet", "Course Syllabus", "Question Paper", "Research Paper"]:
            next_stage = NextStageEnum.SPECIALIZED_HANDLER.value
        else:
            next_stage = NextStageEnum.REJECTED.value

        result = ClassificationResult(
            document_type=document_type,
            confidence=confidence,
            accepted=accepted,
            reasons=reasons,
            evidence=evidence,
            next_stage=next_stage,
            metadata=metadata.to_dict(),
            processing_time_ms=processing_time_ms,
        )

        logger.info(
            "Classification result built",
            document_type=document_type,
            confidence=confidence,
            accepted=accepted,
            next_stage=next_stage,
            duration_ms=processing_time_ms,
        )

        return result
