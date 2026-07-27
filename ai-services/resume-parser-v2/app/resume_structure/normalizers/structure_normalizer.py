"""
Structure Normalizer Engine.
Normalizes headings, casing, spacing, and deduplicates consecutive headings.
"""

from typing import List
from app.resume_structure.schemas.semantic_resume import SectionNode
from core.logging import get_logger

logger = get_logger("structure_normalizer")


class StructureNormalizer:
    """Structure & Unicode Normalization Engine."""

    def normalize_sections(self, sections: List[SectionNode]) -> List[SectionNode]:
        normalized: List[SectionNode] = []
        last_type = None

        for sec in sections:
            # Normalize whitespace and unicode characters in raw_text
            clean_text = sec.raw_text.replace("\r\n", "\n").strip()
            sec.raw_text = clean_text

            # Deduplicate immediate consecutive identical section types
            if sec.canonical_type == last_type and sec.canonical_type not in ["Custom Sections", "Projects"]:
                if normalized:
                    normalized[-1].blocks.extend(sec.blocks)
                    normalized[-1].raw_text += "\n\n" + sec.raw_text
                    normalized[-1].paragraphs_count += sec.paragraphs_count
                    logger.info("Merged consecutive duplicate section", canonical_type=sec.canonical_type)
                    continue

            normalized.append(sec)
            last_type = sec.canonical_type

        return normalized
