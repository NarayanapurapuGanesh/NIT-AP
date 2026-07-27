"""
End-to-End Enterprise Information Extraction Pipeline Engine.
Orchestrates Contact, Experience, Education, Skills, Projects, Publications, Certifications, Awards, Languages,
References, Relationship Engine, and Knowledge Graph Generation.
"""

import time
from app.information_extraction.extractors.awards.award_extractor import AwardExtractor
from app.information_extraction.extractors.certifications.certification_extractor import CertificationExtractor
from app.information_extraction.extractors.contact.contact_extractor import ContactExtractor
from app.information_extraction.extractors.education.education_extractor import EducationExtractor
from app.information_extraction.extractors.experience.experience_extractor import ExperienceExtractor
from app.information_extraction.extractors.languages.language_extractor import LanguageExtractor
from app.information_extraction.extractors.projects.project_extractor import ProjectExtractor
from app.information_extraction.extractors.publications.publication_extractor import PublicationExtractor
from app.information_extraction.extractors.references.reference_extractor import ReferenceExtractor
from app.information_extraction.extractors.skills.skill_extractor import SkillExtractor
from app.information_extraction.knowledge_graph.kg_builder import KnowledgeGraphBuilder
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.resume_structure.schemas.semantic_resume import SemanticResumeModel
from core.logging import get_logger

logger = get_logger("information_extraction_pipeline")


class InformationExtractionPipeline:
    """Enterprise Deterministic Information Extraction Pipeline."""

    def __init__(self) -> None:
        self.contact_extractor = ContactExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.education_extractor = EducationExtractor()
        self.skill_extractor = SkillExtractor()
        self.project_extractor = ProjectExtractor()
        self.publication_extractor = PublicationExtractor()
        self.certification_extractor = CertificationExtractor()
        self.award_extractor = AwardExtractor()
        self.language_extractor = LanguageExtractor()
        self.reference_extractor = ReferenceExtractor()
        self.kg_builder = KnowledgeGraphBuilder()

    async def extract_candidate_profile(self, model: SemanticResumeModel) -> StructuredCandidateProfile:
        """Runs 10 domain extractors and builds candidate knowledge graph."""
        start_time = time.perf_counter()

        # Step 1: Extract Domains
        contact = self.contact_extractor.extract_contact(model)
        experience = self.experience_extractor.extract_experience(model)
        education = self.education_extractor.extract_education(model)
        skills = self.skill_extractor.extract_skills(model)
        projects = self.project_extractor.extract_projects(model)
        publications = self.publication_extractor.extract_publications(model)
        certifications = self.certification_extractor.extract_certifications(model)
        awards = self.award_extractor.extract_awards(model)
        languages = self.language_extractor.extract_languages(model)
        references = self.reference_extractor.extract_references(model)

        # Step 2: Build Knowledge Graph
        kg = self.kg_builder.build_kg(
            doc_uuid=model.document_uuid,
            experiences=experience,
            education=education,
            skills=skills,
            projects=projects,
            publications=publications,
        )

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        profile = StructuredCandidateProfile(
            document_uuid=model.document_uuid,
            filename=model.filename,
            contact=contact,
            experience=experience,
            education=education,
            skills=skills,
            projects=projects,
            publications=publications,
            certifications=certifications,
            awards=awards,
            languages=languages,
            references=references,
            knowledge_graph=kg,
            processing_time_ms=processing_time_ms,
        )

        logger.info(
            "Candidate profile deterministic extraction complete",
            doc_uuid=model.document_uuid,
            candidate_name=contact.full_name.value,
            exp_count=len(experience),
            edu_count=len(education),
            pub_count=len(publications),
            duration_ms=processing_time_ms,
        )

        return profile
