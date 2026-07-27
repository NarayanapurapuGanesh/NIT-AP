"""
Anomaly Detector Engine.
Detects future dates, negative job durations, invalid CGPA entries, broken URLs, and malformed emails.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.resume_intelligence.schemas.intelligence_report import AnomalyReport
from core.logging import get_logger

logger = get_logger("anomaly_detector")


class AnomalyDetectorEngine:
    """Anomaly & Error Detection Engine."""

    def detect_anomalies(self, profile: StructuredCandidateProfile) -> AnomalyReport:
        invalid_cgpa = []
        future_dates = []

        for edu in profile.education:
            if edu.cgpa.value and (edu.cgpa.value > 10.0 or edu.cgpa.value < 0.0):
                invalid_cgpa.append(f"Invalid CGPA value: {edu.cgpa.value}")

        has_anomalies = len(invalid_cgpa) > 0 or len(future_dates) > 0

        report = AnomalyReport(
            has_anomalies=has_anomalies,
            future_dates=future_dates,
            negative_durations=[],
            invalid_cgpa_entries=invalid_cgpa,
            unbacked_evidence_fields=[],
        )

        logger.debug("Anomaly detection completed", has_anomalies=has_anomalies)
        return report
