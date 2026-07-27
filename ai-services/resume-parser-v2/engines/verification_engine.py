from typing import Tuple

from engines.schemas import SpatialLayoutDocument
from extractors.deterministic_extractor import DeterministicEntities
from extractors.link_discovery import ProfileLinks
from services.profile_collector import ProfileEvidencePackage

from validators.fraud_detector import ResumeFraudDetector, FraudDetectionReport
from validators.missing_info_evaluator import MissingInformationEvaluator, QualityEvaluationReport
from validators.profile_verifier import CandidateProfileVerifier, ProfileVerificationReport
from quality.confidence_engine import ConfidenceEngine
from schemas.enterprise_profile import FieldConfidenceScores, EvidencePackageGraph
from evidence.evidence_graph import EvidenceEngine


class VerificationEngine:
    """Engine 4: Verification & Confidence Engine.
    
    Responsible for cross-verifying profiles, detecting fraud, 
    calculating layout-aware confidence scores, and building the evidence graph.
    """
    
    def __init__(self):
        self.profile_verifier = CandidateProfileVerifier()
        self.fraud_detector = ResumeFraudDetector()
        self.missing_evaluator = MissingInformationEvaluator()
        self.confidence_engine = ConfidenceEngine()
        self.evidence_engine = EvidenceEngine()

    def verify_and_score(
        self,
        entities: DeterministicEntities,
        layout_doc: SpatialLayoutDocument,
        profiles: ProfileLinks,
        external_evidence: ProfileEvidencePackage,
        raw_text: str = ""
    ) -> Tuple[
        ProfileVerificationReport, 
        FraudDetectionReport, 
        QualityEvaluationReport, 
        FieldConfidenceScores, 
        EvidencePackageGraph
    ]:
        # 1. Profile Verification (Cross-referencing entities with GitHub/LinkedIn)
        verification_report = self.profile_verifier.verify_profile(entities, external_evidence)
        
        # 2. Fraud Detection
        fraud_report = self.fraud_detector.analyze_fraud(entities, raw_text)
        
        # 3. Missing Information Evaluation
        quality_report = self.missing_evaluator.evaluate_completeness(entities, profiles)
        
        # 4. Confidence Scoring (now correctly uses the SpatialLayoutDocument to apply penalties)
        confidence_scores = self.confidence_engine.compute_confidence(entities, layout_doc)
        
        # 5. Evidence Graph Engine
        evidence_graph = self.evidence_engine.build_evidence_graph(entities, layout_doc, raw_text)

        return verification_report, fraud_report, quality_report, confidence_scores, evidence_graph
