"""
Candidate Intelligence Engine Orchestrator (Modules 1 - 13 Pipeline) — v3.0.

Orchestrates the 13 modular steps of Resume Intelligence Agent v3.0:
1. Smart File Validation
2. Resume Type Detection
3. Deterministic Extraction (v3.0: Section-Aware)
4. Resume Structure Analysis (v3.0: Section Segmentation + Reading Order)
5. Candidate Profile Link Discovery
6. Multi-Source Profile Collector
7. Candidate Profile Verification
8. Resume Fraud Detection
9. Missing Information Detection
10. Qwen2.5 3B Callback LLM (Targeted fallback for low-confidence sections)
11. Unified Enterprise Candidate Profile JSON Schema
12. Field Confidence Engine
13. Evidence Graph Engine

v3.0 Pipeline Flow:
  Upload → Validation → Type Detection → Layout Analysis (sections + reading order)
    → Section-Aware Deterministic Extraction → Confidence Scoring
    → Qwen2.5:3B Callback (uncertain sections only) → Merge
    → Link Discovery → External Collection → Verification → Fraud → Quality
    → Evidence Graph → Enterprise JSON
"""

import re
from typing import Optional
from classifiers.type_detector import ResumeTypeDetector
from evidence.evidence_graph import EvidenceEngine
from extractors.deterministic_extractor import DeterministicExtractor
from extractors.link_discovery import ProfileLinkDiscoveryEngine
from layout.layout_analyzer import LayoutAnalyzer
from llm.qwen_callback import QwenCallbackLLM
from quality.confidence_engine import ConfidenceEngine
from schemas.enterprise_profile import CandidateContact, EnterpriseCandidateProfile
from services.profile_collector import ProfileCollectorService
from validators.file_validator import FileValidator
from validators.fraud_detector import ResumeFraudDetector
from validators.missing_info_evaluator import MissingInformationEvaluator
from validators.profile_verifier import CandidateProfileVerifier


class CandidateIntelligenceEngine:
    """Enterprise Pipeline Orchestrator executing Modules 1 through 13 (v3.0)."""

    def __init__(self, offline_mode: bool = False):
        self.file_validator = FileValidator()
        self.type_detector = ResumeTypeDetector()
        self.layout_analyzer = LayoutAnalyzer()
        self.deterministic_extractor = DeterministicExtractor()
        self.link_discovery = ProfileLinkDiscoveryEngine()
        self.profile_collector = ProfileCollectorService(offline_mode=offline_mode)
        self.profile_verifier = CandidateProfileVerifier()
        self.fraud_detector = ResumeFraudDetector()
        self.missing_evaluator = MissingInformationEvaluator()
        self.qwen_llm = QwenCallbackLLM()
        self.confidence_engine = ConfidenceEngine()
        self.evidence_engine = EvidenceEngine()

    async def analyze_candidate_file(
        self,
        file_bytes: bytes,
        file_name: str
    ) -> EnterpriseCandidateProfile:
        # Module 1: Smart File Validation
        file_meta = self.file_validator.validate_file(file_bytes, file_name)
        if not file_meta.is_valid:
            # Return fail envelope
            return EnterpriseCandidateProfile(
                file_meta=file_meta,
                resume_type=self.type_detector.detect_type(file_bytes, file_meta.file_extension),
                layout_structure=self.layout_analyzer.analyze_document_structure(file_bytes, file_meta.file_extension),
                candidate=CandidateContact(),
                education=[],
                experience=[],
                projects=[],
                skills=[],
                soft_skills=[],
                publications=[],
                patents=[],
                awards=[],
                categorized_awards=[],
                certifications=[],
                profiles=self.link_discovery.discover_links(""),
                external_evidence=await self.profile_collector.collect_profiles(self.link_discovery.discover_links("")),
                verification=self.profile_verifier.verify_profile(self.deterministic_extractor.extract_entities(""), await self.profile_collector.collect_profiles(self.link_discovery.discover_links(""))),
                fraud_report=self.fraud_detector.analyze_fraud(self.deterministic_extractor.extract_entities("")),
                quality_evaluation=self.missing_evaluator.evaluate_completeness(self.deterministic_extractor.extract_entities(""), self.link_discovery.discover_links("")),
                confidence=self.confidence_engine.compute_confidence(self.deterministic_extractor.extract_entities("")),
                evidence=self.evidence_engine.build_evidence_graph(self.deterministic_extractor.extract_entities(""), self.layout_analyzer.analyze_document_structure(file_bytes, file_meta.file_extension)),
            )

        # Raw Text and PDF Hyperlink Annotation extraction
        raw_text, pdf_annotation_links = self.deterministic_extractor.extract_raw_text_and_links(file_bytes, file_meta.file_extension)

        # Module 2: Resume Type Detection
        resume_type = self.type_detector.detect_type(file_bytes, file_meta.file_extension, extracted_text=raw_text)

        # Module 4: Resume Structure Intelligence (v3.0: Section Segmentation + Reading Order)
        layout_structure = self.layout_analyzer.analyze_document_structure(file_bytes, file_meta.file_extension, raw_text=raw_text)

        # Module 3: Deterministic Extraction
        # v3.0: Use section-aware extraction if layout produced sections
        if layout_structure.sections:
            # Use reading_order_text as fallback raw text for contact extraction
            effective_text = layout_structure.reading_order_text or raw_text
            entities = self.deterministic_extractor.extract_entities_from_sections(
                layout_structure.sections,
                raw_text=effective_text,
            )
        else:
            # Fallback to legacy flat text extraction
            entities = self.deterministic_extractor.extract_entities(raw_text)

        # Module 12: Initial Field Confidence Engine Evaluation
        confidence = self.confidence_engine.compute_confidence(entities, layout_structure)

        # Module 10: Callback LLM for low-confidence or uncertain sections
        if confidence.overall_average < 75.0 or entities.uncertain_sections or len(layout_structure.sections) == 0:
            if entities.uncertain_sections:
                for uncertain_para in entities.uncertain_sections[:3]:
                    llm_res = await self.qwen_llm.classify_uncertain_paragraph(uncertain_para)
                    if llm_res.classification == "Skills" and llm_res.extracted_entities:
                        entities.skills = list(set(entities.skills + llm_res.extracted_entities))
                    elif llm_res.classification == "Projects" and llm_res.extracted_entities:
                        from extractors.deterministic_extractor import ProjectEntity
                        for p_title in llm_res.extracted_entities:
                            if not any(p.title.lower() == p_title.lower() for p in entities.projects):
                                entities.projects.append(ProjectEntity(title=p_title, description=uncertain_para[:200]))

            # Re-evaluate confidence post LLM callback enrichment
            confidence = self.confidence_engine.compute_confidence(entities, layout_structure)

        # Module 5: Profile Link Discovery Engine (Text + PDF Hyperlink Annotations)
        profiles = self.link_discovery.discover_links(raw_text, pdf_annotation_links=pdf_annotation_links)

        # Check for Speech Transcript, Event Invitation, Welcome Address, Contact List / Phone Directory, or Non-Resume document
        raw_text_lower = raw_text.lower()
        
        # 1. Phone Directory / Contact List Detection (Multiple phone numbers)
        all_phone_matches = self.deterministic_extractor.PHONE_REGEX.findall(raw_text)
        distinct_phones = set(re.sub(r'\D', '', p) for p in all_phone_matches if len(re.sub(r'\D', '', p)) >= 10)
        is_contact_directory = len(distinct_phones) >= 3

        directory_markers = [
            "contact list", "phone list", "phone directory", "telephone directory",
            "member list", "members list", "roster", "address book", "participants list",
            "attendance sheet", "contact directory", "contacts list"
        ]
        if any(m in raw_text_lower for m in directory_markers):
            is_contact_directory = True

        # 2. Speech / Event Invitation Markers
        speech_markers = [
            "good morning to everyone",
            "good morning",
            "good afternoon",
            "good evening",
            "welcome you all to",
            "on behalf of our institution",
            "guests of honour",
            "welcome to our respected",
            "gracious presence",
            "warmly welcome each one",
            "thank you for joining us",
            "have a wonderful day",
            "vote of thanks",
            "welcome address",
            "chief guest",
            "keynote address",
            "event organized by",
            "ieee women in engineering",
            "affinity group",
        ]
        matched_speech_markers = [m for m in speech_markers if m in raw_text_lower]

        has_single_candidate_contact = (
            bool(entities.email or profiles.linkedin or profiles.github or profiles.google_scholar or profiles.orcid)
            or (bool(entities.phone) and not is_contact_directory)
        )
        has_cv_sections = any(sec.section_name in {"EDUCATION", "EXPERIENCE", "PUBLICATIONS", "PROJECTS", "SKILLS"} for sec in layout_structure.sections)
        has_explicit_cv_title = any(kw in raw_text_lower[:350] for kw in ["curriculum vitae", "faculty cv", "academic cv", "resume", "bio-data"])

        is_speech_or_event_doc = len(matched_speech_markers) >= 2 or (len(matched_speech_markers) >= 1 and not has_single_candidate_contact and not has_explicit_cv_title)
        is_non_resume = (
            is_contact_directory or
            is_speech_or_event_doc or (
                not has_single_candidate_contact
                and not has_explicit_cv_title
                and len(entities.experience) == 0
                and len(entities.publications) == 0
                and not has_cv_sections
            )
        )

        if is_non_resume:
            file_meta.is_valid = False
            file_meta.is_corrupted = False
            if is_contact_directory:
                file_meta.error_message = (
                    f"Document Type Mismatch: The uploaded file '{file_name}' appears to be a Contact List / Phone Directory / Roster "
                    f"(detected {len(distinct_phones)} phone numbers) rather than an individual Candidate Resume/CV. Please upload a valid candidate CV."
                )
            elif is_speech_or_event_doc:
                file_meta.error_message = (
                    f"Document Type Mismatch: The uploaded file '{file_name}' appears to be a Speech Transcript / Event Welcome Address "
                    "rather than a Candidate Resume/CV. Please upload a valid candidate CV or Resume."
                )
            else:
                file_meta.error_message = (
                    f"Non-Resume File Detected: The uploaded file '{file_name}' does not contain valid candidate resume text "
                    "(no contact details, work history, or education sections found). Please upload a valid candidate CV or Resume."
                )
            return EnterpriseCandidateProfile(
                file_meta=file_meta,
                resume_type=resume_type,
                layout_structure=layout_structure,
                candidate=CandidateContact(),
                education=[],
                experience=[],
                projects=[],
                skills=[],
                soft_skills=[],
                publications=[],
                patents=[],
                awards=[],
                categorized_awards=[],
                certifications=[],
                profiles=profiles,
                external_evidence=await self.profile_collector.collect_profiles(profiles),
                verification=self.profile_verifier.verify_profile(entities, await self.profile_collector.collect_profiles(profiles)),
                fraud_report=self.fraud_detector.analyze_fraud(entities),
                quality_evaluation=self.missing_evaluator.evaluate_completeness(entities, profiles),
                confidence=self.confidence_engine.compute_confidence(entities, layout_structure),
                evidence=self.evidence_engine.build_evidence_graph(entities, layout_structure, raw_text),
            )

        # Module 6: Multi-Source Profile Collector
        external_evidence = await self.profile_collector.collect_profiles(profiles)

        # Module 7: Candidate Profile Verification
        verification = self.profile_verifier.verify_profile(entities, external_evidence)

        # Module 8: Resume Fraud Detection Engine
        fraud_report = self.fraud_detector.analyze_fraud(entities, raw_text)

        # Module 9: Missing Information Detection
        quality_evaluation = self.missing_evaluator.evaluate_completeness(entities, profiles)

        # Module 13: Evidence Engine
        evidence_graph = self.evidence_engine.build_evidence_graph(entities, layout_structure, raw_text)

        # Module 11: Enterprise Candidate Profile Schema (v3.0)
        return EnterpriseCandidateProfile(
            file_meta=file_meta,
            resume_type=resume_type,
            layout_structure=layout_structure,
            candidate=CandidateContact(
                name=entities.name,
                email=entities.email,
                phone=entities.phone,
                address=entities.address,
                languages=entities.languages,
                profile_summary=entities.profile_summary,
                candidate_type=entities.candidate_type,
            ),
            education=entities.education,
            experience=entities.experience,
            projects=entities.projects,
            skills=entities.skills,
            soft_skills=entities.soft_skills,
            coding_skills=entities.coding_skills,
            core_interview_points=entities.core_interview_points,
            publications=entities.publications,
            patents=entities.patents,
            awards=entities.awards,
            categorized_awards=entities.categorized_awards,
            certifications=entities.certifications,
            profiles=profiles,
            external_evidence=external_evidence,
            verification=verification,
            fraud_report=fraud_report,
            quality_evaluation=quality_evaluation,
            confidence=confidence,
            evidence=evidence_graph,
        )
