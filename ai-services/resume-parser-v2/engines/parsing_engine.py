import re
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

# We import the schemas from the new engines package
from engines.schemas import SpatialLayoutDocument, SectionBlock

# Re-use the existing entity models for now to preserve the schema output format
from extractors.deterministic_extractor import (
    DeterministicEntities,
    EducationEntity,
    ExperienceEntity,
    PublicationEntity,
    ProjectEntity,
    AchievementEntity,
    DeterministicExtractor
)

class ParsingEngine:
    """Engine 2: Spatial Section Matching & Extraction.
    
    Extracts entities by strictly isolating context to spatial bounding boxes (sections).
    """
    
    def __init__(self):
        # We reuse the heavy lifting regex methods from DeterministicExtractor
        # but orchestrate the extraction spatially.
        self._extractor = DeterministicExtractor()

    def parse_document(self, layout_doc: SpatialLayoutDocument, raw_text: str = "") -> DeterministicEntities:
        """Parses a layout document into structured entities using spatial bounding boxes."""
        
        # If no sections, fallback to legacy text parsing
        if not layout_doc.sections:
            return self._extractor.extract_entities(raw_text or layout_doc.reading_order_text)

        # 1. Map content strictly by spatial section name to prevent cross-contamination
        section_map: Dict[str, List[str]] = {}
        for sec in layout_doc.sections:
            key = sec.section_name
            if key not in section_map:
                section_map[key] = []
            section_map[key].extend(sec.content_lines)

        # If raw_text (which might be OCR'd) is much longer than the layout text (hybrid PDF bug), use raw_text
        reading_text = layout_doc.reading_order_text or ""
        all_text = raw_text if len(raw_text) > len(reading_text) * 1.5 else reading_text
        
        unwrapped_text = self._extractor._unwrap_split_emails(all_text)
        clean_all = self._extractor._clean_pdf_dict_garbage(unwrapped_text)
        all_lines = [line.strip() for line in clean_all.split("\n") if line.strip()]

        # 2. Extract Contact Information
        email = self._extractor._extract_email(clean_all)
        phone = self._extractor._extract_phone(clean_all)
        name = self._extractor._extract_name(all_lines, email)
        address = self._extractor._extract_address(clean_all, section_map.get("CONTACT", []))

        # 3. Extract Explicit Fields bound by their Section Bounding Boxes
        profile_summary = self._extractor._extract_profile_summary(section_map.get("PROFILE", []))
        
        skills_text = "\n".join(section_map.get("SKILLS", []))
        skills = self._extractor._extract_skills(skills_text) if skills_text else self._extractor._extract_skills(clean_all)
        print(f"[DEBUG ParsingEngine] Extracted skills: {skills}")
        if not skills:
            print(f"[DEBUG ParsingEngine] clean_all length: {len(clean_all)}")
            print(f"[DEBUG ParsingEngine] raw_text length: {len(raw_text)}")
            print(f"[DEBUG ParsingEngine] raw_text snippet: {raw_text[:1000]}")
        
        soft_skills_text = "\n".join(section_map.get("SOFT_SKILLS", [])) or skills_text
        soft_skills = self._extractor._extract_soft_skills(soft_skills_text) if soft_skills_text else self._extractor._extract_soft_skills(clean_all)
        
        lang_text = "\n".join(section_map.get("LANGUAGES", []))
        languages = self._extractor._extract_languages(lang_text) if lang_text else self._extractor._extract_languages(clean_all)

        # Spatial Education
        edu_lines = section_map.get("EDUCATION", [])
        edu_text = "\n".join(edu_lines)
        education = self._extractor._extract_education(edu_text, edu_lines) if edu_lines else self._extractor._extract_education(clean_all, all_lines)

        # Spatial Experience
        exp_lines = section_map.get("EXPERIENCE", [])
        experience = self._extractor._extract_experience(exp_lines) if exp_lines else self._extractor._extract_experience(all_lines)

        # Spatial Publications
        pub_lines = section_map.get("PUBLICATIONS", [])
        if pub_lines and hasattr(self._extractor, '_extract_publications_from_section'):
            publications = self._extractor._extract_publications_from_section(pub_lines)
        else:
            publications = self._extractor._extract_publications(pub_lines) if pub_lines else self._extractor._extract_publications(all_lines)

        # Spatial Projects
        proj_lines = section_map.get("PROJECTS", [])
        if proj_lines and hasattr(self._extractor, '_extract_projects_from_section'):
            projects = self._extractor._extract_projects_from_section(proj_lines)
        else:
            projects = self._extractor._extract_projects(proj_lines) if proj_lines else self._extractor._extract_projects(all_lines)

        # Achievements
        award_lines = section_map.get("ACHIEVEMENTS", [])
        awards_flat, categorized_awards = self._extractor._extract_categorized_awards(award_lines) if award_lines else self._extractor._extract_categorized_awards_from_text(all_lines)

        cert_lines = section_map.get("CERTIFICATIONS", [])
        certifications = self._extractor._extract_certifications(cert_lines) if cert_lines else self._extractor._extract_certifications(all_lines)

        patents = self._extractor._extract_patents(all_lines)
        
        # Classification
        candidate_type = self._extractor._classify_candidate_type(experience, education, publications)

        # Identify uncertain blocks for LLM recovery
        uncertain = []
        for sec in layout_doc.sections:
            if sec.section_name == "UNKNOWN" and sec.content_lines:
                combined = " ".join(sec.content_lines)
                if len(combined) > 40:
                    uncertain.append(combined)

        # Coding skills extraction (for coding test generation)
        coding_skills = self._extractor._extract_coding_skills(skills)

        # Core interview points generation
        core_interview_points = self._extractor._generate_core_interview_points(
            name=name, education=education, experience=experience,
            skills=skills, publications=publications, projects=projects,
            awards=awards_flat, candidate_type=candidate_type,
            profile_summary=profile_summary,
        )

        return DeterministicEntities(
            name=name,
            email=email,
            phone=phone,
            address=address,
            profile_summary=profile_summary,
            skills=skills,
            soft_skills=soft_skills,
            coding_skills=coding_skills,
            core_interview_points=core_interview_points,
            education=education,
            experience=experience,
            publications=publications,
            projects=projects,
            patents=patents,
            awards=awards_flat,
            categorized_awards=categorized_awards,
            languages=languages,
            certifications=certifications,
            candidate_type=candidate_type,
            uncertain_sections=uncertain[:5]
        )
