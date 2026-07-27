"""
Feature Flag Engine.
Supports Global and Per-Tenant feature flag evaluation across AI, Analytics, Interview, and Plugin modules.
"""

from typing import Dict, List, Optional
from app.admin.schemas.admin_models import FeatureCategory, FeatureFlagRecord
from core.logging import get_logger

logger = get_logger("feature_flag_engine")


class FeatureFlagEngine:
    """Enterprise Feature Flag Engine."""

    def __init__(self) -> None:
        self._flags: Dict[str, FeatureFlagRecord] = {}
        self._seed_default_feature_flags()

    def _seed_default_feature_flags(self) -> None:
        flags = [
            ("ollama_llm_agent", FeatureCategory.AI_FEATURES, "Local Ollama LLM Reasoning Agent", True),
            ("explainable_ai_audit", FeatureCategory.AI_FEATURES, "Explainable AI Audit Log", True),
            ("ai_interview_question_gen", FeatureCategory.INTERVIEW_FEATURES, "Automated Interview Question Generator", True),
            ("executive_dashboard_forecast", FeatureCategory.ANALYTICS_FEATURES, "Workload Forecasting in Analytics", True),
            ("multi_tenant_custom_branding", FeatureCategory.PLUGINS, "Custom Tenant Branding", True),
            ("experimental_neural_matching", FeatureCategory.EXPERIMENTAL, "Experimental Neural Resume Matching", False),
        ]
        for name, cat, desc, enabled in flags:
            f = FeatureFlagRecord(name=name, category=cat, description=desc, is_enabled_globally=enabled)
            self._flags[name] = f

        logger.info("Seeded default feature flags", count=len(self._flags))

    def is_enabled(self, flag_name: str, tenant_id: Optional[str] = None) -> bool:
        flag = self._flags.get(flag_name)
        if not flag:
            return False

        if tenant_id and tenant_id in flag.tenant_overrides:
            return flag.tenant_overrides[tenant_id]

        return flag.is_enabled_globally

    def list_flags(self) -> List[FeatureFlagRecord]:
        return list(self._flags.values())

    def toggle_flag(self, flag_name: str, is_enabled: bool, tenant_id: Optional[str] = None) -> FeatureFlagRecord:
        flag = self._flags.get(flag_name)
        if not flag:
            flag = FeatureFlagRecord(name=flag_name, category=FeatureCategory.EXPERIMENTAL, is_enabled_globally=is_enabled)
            self._flags[flag_name] = flag

        if tenant_id:
            flag.tenant_overrides[tenant_id] = is_enabled
            logger.info("Feature flag tenant override set", flag_name=flag_name, tenant_id=tenant_id, is_enabled=is_enabled)
        else:
            flag.is_enabled_globally = is_enabled
            logger.info("Feature flag global state updated", flag_name=flag_name, is_enabled=is_enabled)

        return flag
