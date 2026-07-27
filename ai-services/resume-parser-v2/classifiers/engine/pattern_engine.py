"""
Layer 6: Pattern Engine.
Analyzes layout heuristics, density patterns, structural density, page count boundaries, and negative penalties.
"""

from typing import List
from classifiers.engine.metadata_extractor import DocumentMetadata
from classifiers.engine.rule_engine import RuleMatchResult
from classifiers.engine.text_sampler import TextSample
from core.logging import get_logger

logger = get_logger("pattern_engine")


class PatternEngine:
    """Layer 6: Statistical & Structural Pattern Evaluator."""

    def evaluate_patterns(
        self, metadata: DocumentMetadata, text_sample: TextSample
    ) -> List[RuleMatchResult]:
        pattern_matches: List[RuleMatchResult] = []

        # 1. Document Page Count Heuristics
        if metadata.page_count > 35:
            pattern_matches.append(
                RuleMatchResult(
                    doc_type="Book",
                    rule_id="pat_large_page_count",
                    weight=0.35,
                    reason=f"Document has high page count ({metadata.page_count} pages) characteristic of books/manuals",
                )
            )

        # 2. Scanned Image Only Document
        if metadata.is_scanned and metadata.char_count < 100:
            pattern_matches.append(
                RuleMatchResult(
                    doc_type="Certificate",
                    rule_id="pat_scanned_credential",
                    weight=0.20,
                    reason="Scanned image payload with low embedded text density",
                )
            )

        # 3. Heading Density Analysis for Resumes / CVs
        resume_headings = {"education", "experience", "skills", "projects", "publications", "awards"}
        found_headings = [
            h.lower() for h in text_sample.heading_candidates if any(rh in h.lower() for rh in resume_headings)
        ]

        if len(found_headings) >= 3:
            pattern_matches.append(
                RuleMatchResult(
                    doc_type="Curriculum Vitae",
                    rule_id="pat_multi_section_cv",
                    weight=0.20,
                    reason=f"Found {len(found_headings)} standard resume/CV section headings",
                )
            )

        logger.debug("Pattern engine evaluation complete", pattern_matches=len(pattern_matches))
        return pattern_matches
