"""
FacultyIQ Coding Intelligence Agent — Evidence Builder.

Consolidates all assessment data into a structured JSON evidence report
with weighted scoring and overall assessment.
"""

from datetime import datetime, timezone
from typing import Optional

from app.config.settings import settings
from app.core.logging import get_module_logger

log = get_module_logger("evidence")


class EvidenceBuilder:
    """Builds structured evidence reports from assessment data."""

    def __init__(self):
        self.weights = {
            "correctness": settings.pipeline.correctness_weight,
            "complexity": settings.pipeline.complexity_weight,
            "quality": settings.pipeline.quality_weight,
            "explanation": settings.pipeline.explanation_weight,
            "viva": settings.pipeline.viva_weight,
            "debugging": settings.pipeline.debugging_weight,
        }

    def compute_overall_score(
        self,
        correctness_score: float = 0.0,
        complexity_score: float = 0.0,
        quality_score: float = 0.0,
        explanation_score: float = 0.0,
        viva_score: float = 0.0,
        debugging_score: float = 0.0,
    ) -> float:
        """Computes weighted overall score (0-100)."""
        overall = (
            correctness_score * self.weights["correctness"]
            + complexity_score * self.weights["complexity"]
            + quality_score * self.weights["quality"]
            + explanation_score * self.weights["explanation"]
            + viva_score * self.weights["viva"]
            + debugging_score * self.weights["debugging"]
        )
        return round(min(max(overall, 0), 100), 2)

    def build_submission_evidence(
        self,
        question_data: dict,
        submission_data: dict,
        test_results: dict,
        complexity_data: dict,
        static_analysis_data: dict,
        explanation_data: Optional[dict] = None,
        viva_data: Optional[dict] = None,
    ) -> dict:
        """Builds evidence for a single submission."""
        correctness_score = test_results.get("pass_rate", 0)
        complexity_score = complexity_data.get("confidence", 0) * 100
        if complexity_data.get("matches_expected"):
            complexity_score = min(complexity_score + 30, 100)
        quality_score = static_analysis_data.get("maintainability_score", 0)
        explanation_score = (explanation_data or {}).get("overall_score", 0)
        viva_score = 0
        if viva_data and isinstance(viva_data, list):
            scores = [v.get("score", 0) for v in viva_data if isinstance(v, dict)]
            viva_score = sum(scores) / len(scores) if scores else 0

        overall = self.compute_overall_score(
            correctness_score=correctness_score,
            complexity_score=complexity_score,
            quality_score=quality_score,
            explanation_score=explanation_score,
            viva_score=viva_score,
        )

        return {
            "question": {
                "id": question_data.get("id"),
                "title": question_data.get("title"),
                "category": question_data.get("category"),
                "difficulty": question_data.get("difficulty"),
                "bloom_level": question_data.get("bloom_level"),
            },
            "submission": {
                "language": submission_data.get("language"),
                "code_length": len(submission_data.get("source_code", "")),
                "submitted_at": submission_data.get("submitted_at"),
            },
            "test_results": test_results,
            "complexity_analysis": complexity_data,
            "static_analysis": static_analysis_data,
            "explanation_evaluation": explanation_data,
            "viva_evaluation": viva_data,
            "scores": {
                "correctness": round(correctness_score, 1),
                "complexity": round(complexity_score, 1),
                "quality": round(quality_score, 1),
                "explanation": round(explanation_score, 1),
                "viva": round(viva_score, 1),
                "overall": overall,
            },
        }

    def build_session_evidence(
        self,
        session_data: dict,
        submission_evidences: list,
    ) -> dict:
        """Builds the complete session evidence report."""
        if not submission_evidences:
            return {
                "session": session_data,
                "submissions": [],
                "overall_assessment": {
                    "total_score": 0,
                    "questions_attempted": 0,
                    "grade": "F",
                    "recommendation": "No submissions",
                },
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

        scores = [s["scores"]["overall"] for s in submission_evidences]
        avg_score = sum(scores) / len(scores)

        return {
            "session": session_data,
            "submissions": submission_evidences,
            "overall_assessment": {
                "total_score": round(avg_score, 2),
                "questions_attempted": len(submission_evidences),
                "grade": self._compute_grade(avg_score),
                "recommendation": self._compute_recommendation(avg_score),
                "score_breakdown": {
                    "per_question_scores": scores,
                    "highest_score": max(scores),
                    "lowest_score": min(scores),
                },
                "weights_used": self.weights,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "engine_version": settings.app.version,
        }

    def _compute_grade(self, score: float) -> str:
        """Maps score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"

    def _compute_recommendation(self, score: float) -> str:
        """Generates hiring recommendation based on score."""
        if score >= 85:
            return "Strongly Recommended — Exceptional coding ability and problem-solving skills."
        elif score >= 70:
            return "Recommended — Solid coding fundamentals with good analytical thinking."
        elif score >= 55:
            return "Conditional — Adequate skills but may need mentoring in some areas."
        else:
            return "Not Recommended — Below expected threshold for this position."
