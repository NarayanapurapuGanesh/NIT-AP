"""
Document Classification Orchestration Pipeline.
Executes the 9-layer classification sequence asynchronously.
"""

import time
from typing import Any, Dict
from classifiers.base import IClassifier
from classifiers.engine.confidence_scorer import ConfidenceScorer
from classifiers.engine.document_reader import DocumentReader
from classifiers.engine.evidence_collector import EvidenceCollector
from classifiers.engine.input_handler import InputHandler
from classifiers.engine.metadata_extractor import MetadataExtractor
from classifiers.engine.pattern_engine import PatternEngine
from classifiers.engine.result_builder import ClassificationResultBuilder
from classifiers.engine.rule_engine import RuleEngine
from classifiers.engine.text_sampler import TextSampler
from schemas.classification import ClassificationResult
from core.logging import get_logger

logger = get_logger("classification_pipeline")


class DocumentClassificationPipeline(IClassifier):
    """9-Layer Clean Architecture Document Classification Pipeline."""

    def __init__(self) -> None:
        self.input_handler = InputHandler()
        self.document_reader = DocumentReader()
        self.metadata_extractor = MetadataExtractor()
        self.text_sampler = TextSampler()
        self.rule_engine = RuleEngine()
        self.pattern_engine = PatternEngine()
        self.confidence_scorer = ConfidenceScorer()
        self.evidence_collector = EvidenceCollector()
        self.result_builder = ClassificationResultBuilder()

    @property
    def name(self) -> str:
        return "document_classification_pipeline"

    async def classify(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Classifies payload dictionary or returns dict model of ClassificationResult."""
        filename = payload.get("filename", "document.pdf")
        content = payload.get("content", b"")
        result = await self.classify_file(filename, content)
        return result.model_dump()

    async def classify_file(self, filename: str, content: bytes) -> ClassificationResult:
        """Runs the 9-layer classification pipeline on file bytes."""
        start_time = time.perf_counter()

        # Layer 1: Input Handler
        detected_format, filename = self.input_handler.process_input(filename, content)

        # Layer 2: Document Reader
        raw_doc = self.document_reader.read_document(detected_format, content)

        # Layer 3: Metadata Extractor
        metadata = self.metadata_extractor.extract_metadata(raw_doc)

        # Layer 4: Text Sampler
        text_sample = self.text_sampler.sample_text(raw_doc)

        # Layer 5: Rule Engine
        rule_matches = self.rule_engine.evaluate_rules(metadata, text_sample)

        # Layer 6: Pattern Engine
        pattern_matches = self.pattern_engine.evaluate_patterns(metadata, text_sample)

        # Combine Matches
        all_matches = rule_matches + pattern_matches

        # Layer 7: Confidence Scorer
        best_type, confidence, winning_matches = self.confidence_scorer.compute_confidence(all_matches)

        # Layer 8: Evidence Collector
        reasons, evidence = self.evidence_collector.collect_evidence(winning_matches)

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Layer 9: Classification Result Builder
        result = self.result_builder.build_result(
            document_type=best_type,
            confidence=confidence,
            accepted_types=self.rule_engine.accepted_types,
            reasons=reasons,
            evidence=evidence,
            metadata=metadata,
            processing_time_ms=processing_time_ms,
        )

        return result
