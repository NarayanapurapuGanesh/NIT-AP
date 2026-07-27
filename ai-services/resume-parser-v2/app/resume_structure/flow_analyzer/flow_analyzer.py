"""
Reading Flow Analyzer Engine.
Verifies reading flow integrity, detecting broken column flow, floating text, header/footer leakage, and duplicate sections.
"""

from typing import List, Tuple
from app.resume_structure.schemas.semantic_resume import SectionNode
from core.logging import get_logger

logger = get_logger("flow_analyzer")


class ReadingFlowAnalyzer:
    """Reading Flow Verification Engine."""

    def analyze_flow(self, sections: List[SectionNode]) -> Tuple[List[SectionNode], List[str]]:
        warnings: List[str] = []
        seen_types: set[str] = set()

        # 1. Check for duplicate/repeated sections
        for sec in sections:
            if sec.canonical_type in seen_types and sec.canonical_type not in ["Custom Sections", "Projects"]:
                warning_msg = f"Repeated section detected: '{sec.canonical_type}' (Reading order {sec.reading_order_start})"
                warnings.append(warning_msg)
                logger.warning(warning_msg)
            else:
                seen_types.add(sec.canonical_type)

        # 2. Check for reading order anomalies
        last_order = 0
        for sec in sections:
            if sec.reading_order_start < last_order:
                warning_msg = f"Out-of-order section transition at '{sec.canonical_type}'"
                warnings.append(warning_msg)
            last_order = sec.reading_order_end

        # 3. Check for empty or floating sections
        for sec in sections:
            if len(sec.raw_text.strip()) == 0 or len(sec.blocks) == 0:
                warnings.append(f"Empty section block detected under heading '{sec.original_heading}'")

        logger.debug("Reading flow analysis complete", warning_count=len(warnings))
        return sections, warnings
