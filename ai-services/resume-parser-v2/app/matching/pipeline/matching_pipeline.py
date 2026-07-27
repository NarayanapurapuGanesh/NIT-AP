"""
End-to-End Enterprise Candidate-Job Matching Pipeline.
Orchestrates Qualification, Experience, Skills, Research, Teaching, Publications, Certifications,
Domain Matchers, Gap Analysis, Deterministic Scoring Engine, Ranking Features, and Evidence.
"""

import time
from app.matching.certifications.certification_matcher import CertificationMatcher
from app.matching.domain.domain_matcher import DomainMatcher
from app.matching.evidence.match_evidence import MatchEvidenceEngine
from app.matching.experience.experience_matcher import ExperienceMatcher
from app.matching.gap_analysis.gap_analyzer import GapAnalyzerEngine
from app.matching.publications.publication_matcher import PublicationMatcher
from app.matching.qualification.qualification_matcher import QualificationMatcher
from app.matching.ranking.ranking_features import RankingFeatureGenerator
from app.matching.research.research_matcher import ResearchMatcher
from app.matching.schemas.match_models import CandidateMatchReport, MatchAnalysisRequest
from app.matching.scoring.scoring_engine import DeterministicScoringEngine
from app.matching.skills.skill_matcher import SkillMatcher
from app.matching.teaching.teaching_matcher import TeachingMatcher
from core.logging import get_logger

logger = get_logger("matching_pipeline")


class MatchingPipeline:
    """Enterprise Deterministic Candidate-Job Matching Pipeline Engine."""

    def __init__(self) -> None:
        self.qual_matcher = QualificationMatcher()
        self.exp_matcher = ExperienceMatcher()
        self.skill_matcher = SkillMatcher()
        self.research_matcher = ResearchMatcher()
        self.teaching_matcher = TeachingMatcher()
        self.pub_matcher = PublicationMatcher()
        self.cert_matcher = CertificationMatcher()
        self.domain_matcher = DomainMatcher()
        self.gap_analyzer = GapAnalyzerEngine()
        self.scoring_engine = DeterministicScoringEngine()
        self.ranking_generator = RankingFeatureGenerator()
        self.evidence_engine = MatchEvidenceEngine()

    async def match_candidate_to_job(
        self, request: MatchAnalysisRequest
    ) -> CandidateMatchReport:
        """Runs full deterministic matching pipeline."""
        start_time = time.perf_counter()
        cand = request.candidate_profile
        job = request.job_profile

        # Step 1: Run 8 Matchers
        q_score = self.qual_matcher.match_qualification(cand, job)
        e_score = self.exp_matcher.match_experience(cand, job)
        s_score = self.skill_matcher.match_skills(cand, job)
        r_score = self.research_matcher.match_research(cand, job)
        t_score = self.teaching_matcher.match_teaching(cand, job)
        p_score = self.pub_matcher.match_publications(cand, job)
        c_score = self.cert_matcher.match_certifications(cand, job)
        d_score = self.domain_matcher.match_domain(cand, job)

        # Step 2: Gap Analysis
        critical_gaps, matched_reqs, unmatched_reqs = self.gap_analyzer.analyze_gaps(cand, job)

        # Step 3: Compute Overall Score
        breakdown = self.scoring_engine.compute_scores(
            qual_score=q_score,
            exp_score=e_score,
            res_score=r_score,
            teach_score=t_score,
            skill_score=s_score,
            pub_score=p_score,
            cert_score=c_score,
            domain_score=d_score,
            weights=job.weights,
        )

        # Step 4: Generate Ranking Features
        strengths, weaknesses = self.ranking_generator.generate_ranking_features(breakdown)

        # Step 5: Build Evidence
        evidence = self.evidence_engine.build_evidence(cand)

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        report = CandidateMatchReport(
            document_uuid=cand.document_uuid,
            job_uuid=job.job_uuid,
            candidate_name=cand.contact.full_name.value or "Unknown Candidate",
            position_title=job.position.title,
            overall_score=breakdown.overall_score,
            score_breakdown=breakdown,
            strengths=strengths,
            weaknesses=weaknesses,
            critical_gaps=critical_gaps,
            matched_requirements=matched_reqs,
            unmatched_requirements=unmatched_reqs,
            evidence=evidence,
            processing_time_ms=processing_time_ms,
        )

        logger.info(
            "Candidate-Job Matching pipeline complete",
            candidate=report.candidate_name,
            job=job.position.title,
            overall_score=breakdown.overall_score,
            duration_ms=processing_time_ms,
        )

        return report
