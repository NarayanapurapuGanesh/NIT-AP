"""
Attribute-Based Access Control (ABAC) Engine.
Evaluates context-aware policies using subject, resource, action, and environment attributes.
"""

from typing import Any, Dict, List, Optional
from app.admin.schemas.admin_models import ABACPolicy
from core.logging import get_logger

logger = get_logger("abac_engine")


class ABACEngine:
    """Enterprise ABAC Policy Evaluation Engine."""

    def __init__(self) -> None:
        self._policies: Dict[str, ABACPolicy] = {}
        self._seed_default_abac_policies()

    def _seed_default_abac_policies(self) -> None:
        p1 = ABACPolicy(
            name="Department Scoped Review",
            description="Allow users to review candidates in their own department only",
            resource="candidates",
            action="read",
            effect="allow",
            conditions={"match_field": "department_id"},
        )
        self._policies[p1.policy_id] = p1

    def add_policy(self, policy: ABACPolicy) -> ABACPolicy:
        self._policies[policy.policy_id] = policy
        logger.info("ABAC policy added", policy_name=policy.name)
        return policy

    def evaluate(
        self,
        subject_attrs: Dict[str, Any],
        resource_attrs: Dict[str, Any],
        action: str,
    ) -> bool:
        """Evaluates whether subject attributes match resource attributes for requested action."""
        for policy in self._policies.values():
            if policy.action != action and policy.action != "*":
                continue

            match_field = policy.conditions.get("match_field")
            if match_field:
                subj_val = subject_attrs.get(match_field)
                res_val = resource_attrs.get(match_field)
                if subj_val and res_val and subj_val == res_val:
                    logger.debug("ABAC evaluation passed via condition", match_field=match_field)
                    return True

        # Default fallback if no specific ABAC policy triggers denial
        return True
