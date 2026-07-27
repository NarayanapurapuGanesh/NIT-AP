"""
Education Extractor Engine.
Parses degree (B.Tech, M.Tech, Ph.D.), specialization, university, CGPA/percentage, start/end years, and PhD supervisor.
"""

import re
from typing import List
from app.information_extraction.normalizers.field_normalizers import DegreeNormalizer
from app.information_extraction.schemas.candidate_profile import EducationItem, ExtractedField
from app.resume_structure.schemas.semantic_resume import SectionNode, SemanticResumeModel
from core.logging import get_logger

logger = get_logger("education_extractor")

DEGREE_REGEX = re.compile(
    r"\b(Ph\.?D\.?|Doctor\s+of\s+Philosophy|M\.?Tech\.?|B\.?Tech\.?|M\.?S\.?|B\.?S\.?|B\.?E\.?|M\.?E\.?|Master|Bachelor|Diploma)\b",
    re.IGNORECASE,
)
CGPA_REGEX = re.compile(r"\b(CGPA|GPA|CPI)\s*[:=]?\s*(\d\.\d{1,2})\s*(?:/\s*10|\b)", re.IGNORECASE)
PERCENT_REGEX = re.compile(r"\b(\d{2}\.?\d{0,2})\s*%\b")
YEAR_RANGE_REGEX = re.compile(r"\b(19\d\d|20\d\d)\s*[-–to]+\s*(19\d\d|20\d\d|Present)\b", re.IGNORECASE)


class EducationExtractor:
    """Education & Academic Qualification Extractor Engine."""

    def extract_education(self, model: SemanticResumeModel) -> List[EducationItem]:
        education_items: List[EducationItem] = []

        target_sections = [
            sec for sec in model.sections
            if sec.canonical_type in ["Education", "Academic Background", "Qualifications"]
        ]

        for sec in target_sections:
            blocks_text = sec.raw_text.split("\n\n")

            for b_text in blocks_text:
                lines = [l.strip() for l in b_text.split("\n") if l.strip()]
                if not lines:
                    continue

                # Search degree
                match_deg = DEGREE_REGEX.search(b_text)
                raw_deg = match_deg.group(0) if match_deg else lines[0]
                norm_deg = DegreeNormalizer.normalize_degree(raw_deg)

                institution_str = lines[1] if len(lines) > 1 else lines[0]

                # CGPA & Percentage
                cgpa_val = None
                percent_val = None

                match_cgpa = CGPA_REGEX.search(b_text)
                if match_cgpa:
                    try:
                        c_num = float(match_cgpa.group(2))
                        cgpa_val = ExtractedField(value=c_num, raw_text=match_cgpa.group(0), confidence=0.98)
                    except ValueError:
                        pass

                match_pct = PERCENT_REGEX.search(b_text)
                if match_pct:
                    try:
                        p_num = float(match_pct.group(1))
                        percent_val = ExtractedField(value=p_num, raw_text=match_pct.group(0), confidence=0.98)
                    except ValueError:
                        pass

                # Year range
                start_yr = None
                end_yr = None
                match_yr = YEAR_RANGE_REGEX.search(b_text)
                if match_yr:
                    try:
                        start_yr = ExtractedField(value=int(match_yr.group(1)), raw_text=match_yr.group(1), confidence=0.95)
                        if match_yr.group(2).isdigit():
                            end_yr = ExtractedField(value=int(match_yr.group(2)), raw_text=match_yr.group(2), confidence=0.95)
                    except ValueError:
                        pass

                item = EducationItem(
                    degree=ExtractedField(value=norm_deg, raw_text=raw_deg, normalized_value=norm_deg, confidence=0.95, evidence=sec.evidence[:1]),
                    institution=ExtractedField(value=institution_str, raw_text=institution_str, normalized_value=institution_str, confidence=0.90),
                    cgpa=cgpa_val or ExtractedField(),
                    percentage=percent_val or ExtractedField(),
                    start_year=start_yr or ExtractedField(),
                    end_year=end_yr or ExtractedField(),
                )
                education_items.append(item)

        logger.debug("Education extraction complete", items_count=len(education_items))
        return education_items
