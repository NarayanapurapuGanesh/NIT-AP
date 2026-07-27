"""
Document Intelligence Orchestrator (v3.1 5-Engine Architecture).

Replaces the monolithic CandidateIntelligenceEngine with a clean, 
strict state machine that routes data between the 5 micro-engines.
"""

from typing import Optional
import asyncio

from validators.file_validator import FileValidator
from classifiers.type_detector import ResumeTypeDetector
from schemas.enterprise_profile import EnterpriseCandidateProfile, CandidateContact

from engines.document_ai_engine import DocumentAIEngine
from engines.parsing_engine import ParsingEngine
from engines.enrichment_engine import EnrichmentEngine
from engines.verification_engine import VerificationEngine
from engines.callback_llm_engine import CallbackLLMEngine


class DocumentIntelligenceOrchestrator:
    """Orchestrates the 5-Engine v3.1 Architecture."""
    
    def __init__(self, offline_mode: bool = False):
        self.file_validator = FileValidator()
        self.type_detector = ResumeTypeDetector()
        
        # Instantiate the 5 engines
        self.engine1_doc_ai = DocumentAIEngine()
        self.engine2_parsing = ParsingEngine()
        self.engine3_enrichment = EnrichmentEngine(offline_mode=offline_mode)
        self.engine4_verification = VerificationEngine()
        self.engine5_callback_llm = CallbackLLMEngine()

    async def analyze_candidate_file(
        self,
        file_bytes: bytes,
        file_name: str
    ) -> EnterpriseCandidateProfile:
        # Pre-flight: File Validation
        file_meta = self.file_validator.validate_file(file_bytes, file_name)
        file_ext = file_meta.file_extension
        
        if not file_meta.is_valid:
            return self._build_fail_envelope(file_meta)

        # Pre-flight: Basic Type Detection
        resume_type = self.type_detector.detect_type(file_bytes, file_ext)

        # =====================================================================
        # ENGINE 1: Document AI (Layout & Spatial Extraction)
        # =====================================================================
        # Note: raw text is used as a fallback if PDF parsing fails visually
        raw_text_fallback, pdf_links = self.engine2_parsing._extractor.extract_raw_text_and_links(file_bytes, file_ext)
        
        spatial_doc = self.engine1_doc_ai.analyze_document(
            document_bytes=file_bytes,
            file_extension=file_ext,
            raw_text=raw_text_fallback
        )

        # =====================================================================
        # ENGINE 2: Parsing Engine (Spatial Section Matching)
        # =====================================================================
        entities = self.engine2_parsing.parse_document(
            layout_doc=spatial_doc, 
            raw_text=raw_text_fallback
        )
        
        # Check for Non-Resume file early exit
        if not entities.email and not entities.phone and not entities.skills and not entities.education:
            file_meta.is_valid = False
            file_meta.is_corrupted = True
            file_meta.error_message = "Non-Resume File Detected: No core resume entities found."
            return self._build_fail_envelope(file_meta)

        # =====================================================================
        # ENGINE 3: Enrichment Engine
        # =====================================================================
        profiles, external_evidence = await self.engine3_enrichment.enrich_profile(
            raw_text=raw_text_fallback, 
            pdf_annotation_links=pdf_links
        )

        # =====================================================================
        # ENGINE 4: Verification Engine (Initial Pass)
        # =====================================================================
        # We run this before LLM callback to get the layout-aware confidence score
        verification_report, fraud_report, quality_report, confidence, evidence_graph = self.engine4_verification.verify_and_score(
            entities=entities,
            layout_doc=spatial_doc,
            profiles=profiles,
            external_evidence=external_evidence,
            raw_text=raw_text_fallback
        )

        # =====================================================================
        # ENGINE 5: Callback LLM Engine (Targeted Recovery)
        # =====================================================================
        # If confidence < 85%, sections missing, or key entities incomplete, invoke LLM
        needs_llm_recovery = (
            confidence.overall_average < 85.0 or 
            len(spatial_doc.sections) == 0 or 
            bool(entities.uncertain_sections) or
            len(entities.skills) < 3 or
            not entities.experience
        )
        if needs_llm_recovery:
            entities = await self.engine5_callback_llm.recover_entities(
                entities=entities,
                confidence=confidence,
                layout_doc=spatial_doc
            )
            
            # Re-run Engine 4 verification post-recovery
            verification_report, fraud_report, quality_report, confidence, evidence_graph = self.engine4_verification.verify_and_score(
                entities=entities,
                layout_doc=spatial_doc,
                profiles=profiles,
                external_evidence=external_evidence,
                raw_text=raw_text_fallback
            )

        # Build final Enterprise Schema DTO
        return EnterpriseCandidateProfile(
            file_meta=file_meta,
            resume_type=resume_type,
            # We map SpatialLayoutDocument back to StructuralAnalysisResult schema format for API compatibility
            layout_structure=spatial_doc, 
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
            verification=verification_report,
            fraud_report=fraud_report,
            quality_evaluation=quality_report,
            confidence=confidence,
            evidence=evidence_graph,
        )

    def _build_fail_envelope(self, file_meta) -> EnterpriseCandidateProfile:
        """Returns an empty profile shell with error metadata if parsing critically fails."""
        from layout.layout_analyzer import StructuralAnalysisResult
        from extractors.link_discovery import ProfileLinks
        from services.profile_collector import ProfileEvidencePackage
        from validators.profile_verifier import ProfileVerificationReport
        from validators.fraud_detector import FraudDetectionReport
        from validators.missing_info_evaluator import QualityEvaluationReport
        from schemas.enterprise_profile import FieldConfidenceScores, EvidencePackageGraph
        from classifiers.type_detector import ResumeTypeResult, ResumeCategory
        
        return EnterpriseCandidateProfile(
            file_meta=file_meta,
            resume_type=ResumeTypeResult(category=ResumeCategory.DIGITAL_PDF, confidence=0.0),
            layout_structure=StructuralAnalysisResult(),
            candidate=CandidateContact(),
            education=[], experience=[], projects=[], skills=[], soft_skills=[],
            coding_skills=[], core_interview_points=[],
            publications=[], patents=[], awards=[], categorized_awards=[], certifications=[],
            profiles=ProfileLinks(),
            external_evidence=ProfileEvidencePackage(),
            verification=ProfileVerificationReport(match_score=0.0, alerts=[]),
            fraud_report=FraudDetectionReport(risk_score=0.0, risk_level="Low", flags=[]),
            quality_evaluation=QualityEvaluationReport(completeness_score=0.0, missing_critical_fields=[]),
            confidence=FieldConfidenceScores(),
            evidence=EvidencePackageGraph()
        )
