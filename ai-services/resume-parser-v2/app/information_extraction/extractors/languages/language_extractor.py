"""
Language Extractor Engine.
Parses known languages and proficiency levels.
"""

from typing import List
from app.information_extraction.schemas.candidate_profile import LanguageItem
from app.resume_structure.schemas.semantic_resume import SectionNode, SemanticResumeModel
from core.logging import get_logger

logger = get_logger("language_extractor")

KNOWN_LANGUAGES = ["English", "Hindi", "Telugu", "Tamil", "Bengali", "Spanish", "French", "German", "Japanese", "Mandarin"]


class LanguageExtractor:
    """Languages Extractor Engine."""

    def extract_languages(self, model: SemanticResumeModel) -> List[LanguageItem]:
        languages: List[LanguageItem] = []

        target_sections = [
            sec for sec in model.sections if sec.canonical_type in ["Languages"]
        ]

        full_text = "\n".join(sec.raw_text for sec in target_sections) if target_sections else ""

        for lang in KNOWN_LANGUAGES:
            import re
            if re.search(r"\b" + re.escape(lang) + r"\b", full_text, re.IGNORECASE):
                languages.append(LanguageItem(language=lang, proficiency="Professional"))

        logger.debug("Language extraction complete", count=len(languages))
        return languages
