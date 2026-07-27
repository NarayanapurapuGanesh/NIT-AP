"""
End-to-End Enterprise Resume Intelligence & Validation Pipeline Engine.
Orchestrates Profile Validation, Timeline & Career Gap Analysis, Domain Intelligence, Quality Scoring,
Consistency Checks, Anomaly Detection, Evidence Verification, Statistics Aggregation, and Recommendations.
"""

import time
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.resume_intelligence.anomalies.anomaly_detector import AnomalyDetectorEngine
from app.resume_intelligence.certifications.certification_intelligence import CertificationIntelligenceEngine
from app.resume_intelligence.consistency.consistency_engine import ConsistencyEngine
from app.resume_intelligence.education.education_intelligence import EducationIntelligenceEngine
from app.resume_intelligence.employment.employment_intelligence import EmploymentIntelligenceEngine
from app.resume_intelligence.evidence.evidence_verifier import EvidenceVerifierEngine
from app.resume_intelligence.publications.publication_intelligence import PublicationIntelligenceEngine
from app.resume_intelligence.quality.quality_engine import ResumeQualityEngine
from app.resume_intelligence.recommendations.recommendation_engine import RecommendationEngine
from app.resume_intelligence.research.research_intelligence import ResearchIntelligenceEngine
from app.resume_intelligence.schemas.intelligence_report import CandidateIntelligenceReport
from app.resume_intelligence.skills.skill_intelligence import SkillIntelligenceEngine
from app.resume_intelligence.statistics.statistics_engine import IntelligenceStatisticsEngine
from app.resume_intelligence.teaching.teaching_intelligence import TeachingIntelligenceEngine
from app.resume_intelligence.timeline.timeline_analyzer import TimelineAnalyzerEngine
from app.resume_intelligence.validators.profile_validator import ProfileValidatorEngine
from core.logging import get_logger

logger = get_logger("resume_intelligence_pipeline")


class ResumeIntelligencePipeline:
    """Enterprise Deterministic Resume Intelligence & Validation Pipeline Engine."""

    def __init__(self) -> None:
        self.profile_validator = ProfileValidatorEngine()
        self.timeline_analyzer = TimelineAnalyzerEngine()
        self.employment_intel = EmploymentIntelligenceEngine()
        self.education_intel = EducationIntelligenceEngine()
        self.skill_intel = SkillIntelligenceEngine()
        self.research_intel = ResearchIntelligenceEngine()
        self.teaching_intel = TeachingIntelligenceEngine()
        self.publication_intel = PublicationIntelligenceEngine()
        self.certification_intel = CertificationIntelligenceEngine()
        self.quality_engine = ResumeQualityEngine()
        self.consistency_engine = ConsistencyEngine()
        self.anomaly_detector = AnomalyDetectorEngine()
        self.evidence_verifier = EvidenceVerifierEngine()
        self.statistics_engine = IntelligenceStatisticsEngine()
        self.recommendation_engine = RecommendationEngine()

    async def generate_intelligence_report(
        self, profile: StructuredCandidateProfile
    ) -> CandidateIntelligenceReport:
        """Executes full intelligence pipeline and returns canonical CandidateIntelligenceReport."""
        start_time = time.perf_counter()

        # Step 1: Profile Validation
        val_warnings, val_errors = self.profile_validator.validate_profile(profile)

        # Step 2: Timeline Analysis
        timeline = self.timeline_analyzer.analyze_timeline(profile)

        # Step 3: Domain Intelligences
        emp_meta = self.employment_intel.analyze_employment(profile)
        edu_meta = self.education_intel.analyze_education(profile)
        skill_meta = self.skill_intel.analyze_skills(profile)
        research = self.research_intel.analyze_research(profile)
        teaching = self.teaching_intel.analyze_teaching(profile)
        pub_meta = self.publication_intel.analyze_publications(profile)
        cert_meta = self.certification_intel.analyze_certifications(profile)

        # Step 4: Consistency & Anomaly Detection
        consistency = self.consistency_engine.analyze_consistency(profile)
        anomalies = self.anomaly_detector.detect_anomalies(profile)

        # Step 5: Evidence Verification
        unbacked_fields = self.evidence_verifier.verify_evidence(profile)
        if unbacked_fields:
            anomalies.unbacked_evidence_fields = unbacked_fields

        # Step 6: Quality Scoring
        scores = self.quality_engine.compute_quality_scores(
            profile=profile,
            timeline=timeline,
            research=research,
            teaching=teaching,
            errors_count=len(val_errors),
        )

        # Step 7: Statistics Aggregation
        metrics = self.statistics_engine.compile_statistics(profile, timeline)
        metrics["highest_qualification"] = edu_meta["highest_qualification"]
        metrics["has_phd"] = edu_meta["has_phd"]

        # Step 8: Recommendation Generation
        recommendations = self.recommendation_engine.generate_recommendations(
            profile=profile,
            timeline=timeline,
            scores=scores,
            unbacked_fields=unbacked_fields,
        )

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        report = CandidateIntelligenceReport(
            document_uuid=profile.document_uuid,
            filename=profile.filename,
            candidate_name=profile.contact.full_name.value or "Unknown Candidate",
            scores=scores,
            timeline=timeline,
            research=research,
            teaching=teaching,
            consistency=consistency,
            anomalies=anomalies,
            recommendations=recommendations,
            warnings=val_warnings + pub_meta.get("duplicate_warnings", []),
            errors=val_errors,
            metrics_summary=metrics,
            processing_time_ms=processing_time_ms,
        )

        logger.info(
            "Candidate intelligence report generated cleanly",
            doc_uuid=profile.document_uuid,
            candidate_name=report.candidate_name,
            overall_quality=scores.resume_quality_score,
            duration_ms=processing_time_ms,
        )

        return report
