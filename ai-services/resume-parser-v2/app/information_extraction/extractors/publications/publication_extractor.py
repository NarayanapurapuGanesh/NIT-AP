"""
Publication Extractor Engine.
Parses scholarly paper titles, authors list, journal/conference venues, publication year, and DOI.
"""

import re
from typing import List
from app.information_extraction.schemas.candidate_profile import ExtractedField, PublicationItem
from app.resume_structure.schemas.semantic_resume import SectionNode, SemanticResumeModel
from core.logging import get_logger

logger = get_logger("publication_extractor")

DOI_REGEX = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
YEAR_REGEX = re.compile(r"\b(19\d\d|20\d\d)\b")


class PublicationExtractor:
    """Scholarly Publications Extractor Engine."""

    def extract_publications(self, model: SemanticResumeModel) -> List[PublicationItem]:
        publication_items: List[PublicationItem] = []

        target_sections = [
            sec for sec in model.sections
            if sec.canonical_type in ["Publications", "Books", "Conferences", "Workshops"]
        ]

        for sec in target_sections:
            lines = [l.strip() for l in sec.raw_text.split("\n") if l.strip()]

            for line in lines:
                if len(line) < 25:
                    continue

                # Search DOI
                doi_val = None
                match_doi = DOI_REGEX.search(line)
                if match_doi:
                    raw_doi = match_doi.group(0)
                    doi_val = ExtractedField(value=raw_doi, raw_text=raw_doi, confidence=0.99)

                # Search Year
                year_val = None
                match_yr = YEAR_REGEX.search(line)
                if match_yr:
                    try:
                        y_num = int(match_yr.group(1))
                        year_val = ExtractedField(value=y_num, raw_text=match_yr.group(1), confidence=0.95)
                    except ValueError:
                        pass

                item = PublicationItem(
                    title=ExtractedField(value=line, raw_text=line, normalized_value=line, confidence=0.85, evidence=sec.evidence[:1]),
                    year=year_val or ExtractedField(),
                    doi=doi_val or ExtractedField(),
                )
                publication_items.append(item)

        logger.debug("Publication extraction complete", items_count=len(publication_items))
        return publication_items
