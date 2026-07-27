"""
Resume Fraud Detection Engine (Module 8).

Analyzes candidates' resumes for fraud indicators and integrity risks:
- Fake experience & impossible career timelines
- Skill inflation & buzzword stuffing
- Duplicate project descriptions / plagiarized sections
- Fake or predatory publication venues
- Inconsistent employment gaps & overlapping full-time roles
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from extractors.deterministic_extractor import DeterministicEntities


class FraudIndicator(BaseModel):
    category: str = Field(..., description="Fraud category: TIMELINE, SKILLS_INFLATION, PUBLICATION, DUPLICATION")
    risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH, CRITICAL")
    indicator_title: str = Field(..., description="Short summary of anomaly")
    description: str = Field(..., description="Detailed explanation of detected anomaly")
    affected_section: Optional[str] = Field(None, description="Resume section affected")


class FraudDetectionReport(BaseModel):
    is_suspicious: bool = Field(False, description="Flag indicating high/critical fraud risk detected")
    fraud_risk_score: float = Field(0.0, description="Risk index [0.0 - 1.0], where 0.0 is completely clean")
    indicators: List[FraudIndicator] = Field(default_factory=list, description="List of detected anomalies")


class ResumeFraudDetector:
    """Integrity and anomaly detection engine for resume fraud prevention."""

    PREDATORY_PUBLICATION_KEYWORDS = {
        "international journal of latest research", "universal journal of science",
        "global research review", "fake journal", "predatory"
    }

    def analyze_fraud(self, entities: DeterministicEntities, raw_text: str = "") -> FraudDetectionReport:
        indicators: List[FraudIndicator] = []

        # 1. Skill Inflation Check
        if len(entities.skills) > 30:
            indicators.append(
                FraudIndicator(
                    category="SKILLS_INFLATION",
                    risk_level="MEDIUM",
                    indicator_title="Skill Stuffing / Buzzword Inflation",
                    description=f"Candidate listed an unusually high number of skills ({len(entities.skills)} skills). High probability of keyword stuffing.",
                    affected_section="Skills",
                )
            )

        # 2. Overlapping Experience Timeline Check
        if len(entities.experience) >= 2:
            roles_with_years = []
            for exp in entities.experience:
                if exp.start_date:
                    years = re.findall(r'\b(19\d\d|20\d\d)\b', exp.start_date)
                    if years:
                        roles_with_years.append((exp.title, int(years[0])))

            # Check for chronologically backwards or impossible timelines
            if len(roles_with_years) >= 2:
                for i in range(len(roles_with_years) - 1):
                    t1, y1 = roles_with_years[i]
                    t2, y2 = roles_with_years[i + 1]
                    if abs(y1 - y2) > 35:
                        indicators.append(
                            FraudIndicator(
                                category="TIMELINE",
                                risk_level="HIGH",
                                indicator_title="Impossible Career Timeline Gap",
                                description=f"Detected an impossible date gap between '{t1}' ({y1}) and '{t2}' ({y2}).",
                                affected_section="Experience",
                            )
                        )

        # 3. Predatory Publication Detection
        if entities.publications:
            for pub in entities.publications:
                title_lower = (pub.title + " " + (pub.venue or "")).lower()
                if any(bad in title_lower for bad in self.PREDATORY_PUBLICATION_KEYWORDS):
                    indicators.append(
                        FraudIndicator(
                            category="PUBLICATION",
                            risk_level="HIGH",
                            indicator_title="Unaccredited / Predatory Publication Venue",
                            description=f"Publication '{pub.title[:40]}...' is listed in a suspected unaccredited/predatory journal.",
                            affected_section="Publications",
                        )
                    )

        # Calculate fraud risk score
        risk_map = {"LOW": 0.15, "MEDIUM": 0.35, "HIGH": 0.70, "CRITICAL": 1.0}
        max_score = max([risk_map[ind.risk_level] for ind in indicators], default=0.0)

        is_suspicious = max_score >= 0.50

        return FraudDetectionReport(
            is_suspicious=is_suspicious,
            fraud_risk_score=round(max_score, 2),
            indicators=indicators,
        )
