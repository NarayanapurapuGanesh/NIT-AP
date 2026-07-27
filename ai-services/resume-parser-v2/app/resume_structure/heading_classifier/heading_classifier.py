"""
Heading Classifier & Misspelling Normalizer Engine.
Classifies detected headings into 40+ canonical section categories using exact matching, regex, and Levenshtein distance.
"""

from typing import Tuple
from app.resume_structure.heading_detector.heading_detector import DetectedHeadingCandidate
from app.resume_structure.ontology.taxonomy import SectionTaxonomyResolver
from core.logging import get_logger

logger = get_logger("heading_classifier")


def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class ClassifiedHeading:
    def __init__(
        self,
        candidate: DetectedHeadingCandidate,
        canonical_type: str,
        confidence: float,
        priority: int,
        is_misspelled: bool = False,
        matched_alias: str = "",
    ) -> None:
        self.candidate = candidate
        self.canonical_type = canonical_type
        self.confidence = confidence
        self.priority = priority
        self.is_misspelled = is_misspelled
        self.matched_alias = matched_alias


class HeadingClassifier:
    """Heading Classification & Misspelling Normalizer Engine."""

    def __init__(self) -> None:
        self.taxonomy = SectionTaxonomyResolver()

    def classify_heading(self, candidate: DetectedHeadingCandidate) -> ClassifiedHeading:
        raw_text = candidate.raw_text.strip()
        c_type, alias, prio = self.taxonomy.resolve(raw_text)

        if c_type != "Custom Sections":
            return ClassifiedHeading(
                candidate=candidate,
                canonical_type=c_type,
                confidence=min(1.0, candidate.score * 0.95 + 0.15),
                priority=prio,
                is_misspelled=False,
                matched_alias=alias,
            )

        # Levenshtein misspelling check against standard aliases
        clean_text = raw_text.lower()
        best_match, best_dist = self._find_fuzzy_match(clean_text)

        if best_match and best_dist <= 2 and len(clean_text) > 4:
            fuzzy_type, _, fuzzy_prio = self.taxonomy.resolve(best_match)
            logger.info("Fuzzy misspelling heading normalized", original=raw_text, normalized=fuzzy_type)
            return ClassifiedHeading(
                candidate=candidate,
                canonical_type=fuzzy_type,
                confidence=0.82,
                priority=fuzzy_prio,
                is_misspelled=True,
                matched_alias=best_match,
            )

        # Fallback to Custom Section
        return ClassifiedHeading(
            candidate=candidate,
            canonical_type="Custom Sections",
            confidence=0.50,
            priority=999,
            is_misspelled=False,
            matched_alias=raw_text,
        )

    def _find_fuzzy_match(self, clean_text: str) -> Tuple[str | None, int]:
        best_alias = None
        min_dist = 999

        for alias in self.taxonomy._alias_map.keys():
            if abs(len(clean_text) - len(alias)) > 3:
                continue
            dist = levenshtein_distance(clean_text, alias)
            if dist < min_dist:
                min_dist = dist
                best_alias = alias

        return best_alias, min_dist
