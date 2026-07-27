"""
Contact Extractor Engine.
Parses full name, email, phone number, LinkedIn, GitHub, Google Scholar, ORCID, and portfolio URLs from Header/Summary blocks.
"""

import re
from app.information_extraction.normalizers.field_normalizers import ContactNormalizer, NameNormalizer
from app.information_extraction.schemas.candidate_profile import ContactInfo, ExtractedField
from app.resume_structure.schemas.semantic_resume import SectionNode, SemanticResumeModel
from core.logging import get_logger

logger = get_logger("contact_extractor")

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
LINKEDIN_REGEX = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+", re.IGNORECASE)
GITHUB_REGEX = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+", re.IGNORECASE)
SCHOLAR_REGEX = re.compile(r"(?:https?://)?scholar\.google\.[a-z.]+/citations\?[^\s]+", re.IGNORECASE)
ORCID_REGEX = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b")


class ContactExtractor:
    """Contact & Identity Details Extractor Engine."""

    def extract_contact(self, model: SemanticResumeModel) -> ContactInfo:
        contact = ContactInfo()

        # Target Header block or first section
        search_text = ""
        evidence_points = []

        if model.header_block:
            search_text = model.header_block.raw_text
            evidence_points = model.header_block.evidence
        elif model.sections:
            search_text = model.sections[0].raw_text
            evidence_points = model.sections[0].evidence

        # 1. Full Name Extraction (First non-empty line of header)
        lines = [line.strip() for line in search_text.split("\n") if line.strip()]
        if lines:
            raw_name = lines[0]
            full, first, middle, last = NameNormalizer.normalize_name(raw_name)
            contact.full_name = ExtractedField(value=full, raw_text=raw_name, normalized_value=full, confidence=0.92, evidence=evidence_points[:1])
            contact.first_name = ExtractedField(value=first, raw_text=first, normalized_value=first, confidence=0.90)
            contact.middle_name = ExtractedField(value=middle, raw_text=middle, normalized_value=middle, confidence=0.90)
            contact.last_name = ExtractedField(value=last, raw_text=last, normalized_value=last, confidence=0.90)

            if len(lines) > 1 and not EMAIL_REGEX.search(lines[1]):
                contact.professional_title = ExtractedField(value=lines[1], raw_text=lines[1], normalized_value=lines[1], confidence=0.85)

        # 2. Email
        match_email = EMAIL_REGEX.search(search_text)
        if match_email:
            raw_e = match_email.group(0)
            norm_e = ContactNormalizer.normalize_email(raw_e)
            contact.email = ExtractedField(value=norm_e, raw_text=raw_e, normalized_value=norm_e, confidence=0.98, evidence=evidence_points[:1])

        # 3. Phone
        match_phone = PHONE_REGEX.search(search_text)
        if match_phone:
            raw_p = match_phone.group(0)
            norm_p = ContactNormalizer.normalize_phone(raw_p)
            contact.phone = ExtractedField(value=norm_p, raw_text=raw_p, normalized_value=norm_p, confidence=0.95, evidence=evidence_points[:1])

        # 4. LinkedIn
        match_li = LINKEDIN_REGEX.search(search_text)
        if match_li:
            raw_li = match_li.group(0)
            norm_li = ContactNormalizer.normalize_url(raw_li)
            contact.linkedin_url = ExtractedField(value=norm_li, raw_text=raw_li, normalized_value=norm_li, confidence=0.98)

        # 5. GitHub
        match_gh = GITHUB_REGEX.search(search_text)
        if match_gh:
            raw_gh = match_gh.group(0)
            norm_gh = ContactNormalizer.normalize_url(raw_gh)
            contact.github_url = ExtractedField(value=norm_gh, raw_text=raw_gh, normalized_value=norm_gh, confidence=0.98)

        # 6. Google Scholar
        match_gs = SCHOLAR_REGEX.search(search_text)
        if match_gs:
            raw_gs = match_gs.group(0)
            norm_gs = ContactNormalizer.normalize_url(raw_gs)
            contact.google_scholar_url = ExtractedField(value=norm_gs, raw_text=raw_gs, normalized_value=norm_gs, confidence=0.98)

        # 7. ORCID
        match_orcid = ORCID_REGEX.search(search_text)
        if match_orcid:
            raw_o = match_orcid.group(0)
            contact.orcid = ExtractedField(value=raw_o, raw_text=raw_o, normalized_value=raw_o, confidence=0.99)

        logger.debug("Contact extraction completed", full_name=contact.full_name.value, email=contact.email.value)
        return contact
