"""
Layer 5: Rule Engine.
Loads versioned classification rules from external JSON configurations and evaluates boolean rule predicates.
"""

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Tuple
from classifiers.engine.metadata_extractor import DocumentMetadata
from classifiers.engine.text_sampler import TextSample
from core.exceptions import ConfigurationError
from core.logging import get_logger

logger = get_logger("rule_engine")


class RuleMatchResult:
    def __init__(self, doc_type: str, rule_id: str, weight: float, reason: str, matched_text: str | None = None) -> None:
        self.doc_type = doc_type
        self.rule_id = rule_id
        self.weight = weight
        self.reason = reason
        self.matched_text = matched_text


class RuleEngine:
    """Layer 5: Rule Evaluator Engine."""

    def __init__(self, rules_filepath: str | Path | None = None) -> None:
        if rules_filepath is None:
            rules_filepath = Path(__file__).parents[2] / "config" / "rules" / "v1" / "classification_rules.json"

        self.rules_filepath = Path(rules_filepath)
        self.rules_config = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        if not self.rules_filepath.exists():
            raise ConfigurationError(
                f"Classification rules file missing at path: {self.rules_filepath}",
                details={"filepath": str(self.rules_filepath)},
            )
        try:
            with open(self.rules_filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            raise ConfigurationError(
                f"Failed to parse classification rules JSON: {str(exc)}",
                details={"filepath": str(self.rules_filepath)},
            ) from exc

    def evaluate_rules(
        self, metadata: DocumentMetadata, text_sample: TextSample
    ) -> List[RuleMatchResult]:
        """Evaluates all configured rules against extracted metadata and text samples."""
        match_results: List[RuleMatchResult] = []
        doc_rules = self.rules_config.get("document_rules", [])

        for doc_def in doc_rules:
            doc_type = doc_def["type"]
            rules = doc_def.get("rules", [])

            for rule in rules:
                rule_id = rule["id"]
                rule_type = rule["type"]
                pattern = rule.get("pattern")
                weight = float(rule.get("weight", 0.10))
                reason = rule.get("reason", f"Matched {rule_id}")

                matched, matched_text = self._evaluate_single_rule(
                    rule_type=rule_type,
                    pattern=pattern,
                    metadata=metadata,
                    text_sample=text_sample,
                )

                if matched:
                    match_results.append(
                        RuleMatchResult(
                            doc_type=doc_type,
                            rule_id=rule_id,
                            weight=weight,
                            reason=reason,
                            matched_text=matched_text,
                        )
                    )

        logger.debug("Rule engine evaluation completed", total_matches=len(match_results))
        return match_results

    def _evaluate_single_rule(
        self, rule_type: str, pattern: str | None, metadata: DocumentMetadata, text_sample: TextSample
    ) -> Tuple[bool, str | None]:
        if not pattern:
            return False, None

        compiled_regex = re.compile(pattern, re.MULTILINE | re.IGNORECASE)

        if rule_type == "header_regex":
            match = compiled_regex.search(text_sample.header_text)
            if match:
                return True, match.group(0)

        elif rule_type == "heading_regex":
            for heading in text_sample.heading_candidates:
                match = compiled_regex.search(heading)
                if match:
                    return True, match.group(0)

        elif rule_type == "keyword_regex":
            match = compiled_regex.search(text_sample.full_text)
            if match:
                return True, match.group(0)

        elif rule_type == "footer_regex":
            match = compiled_regex.search(text_sample.footer_text)
            if match:
                return True, match.group(0)

        return False, None

    @property
    def accepted_types(self) -> List[str]:
        return self.rules_config.get("accepted_types", [])
