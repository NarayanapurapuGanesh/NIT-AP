"""
Configuration Center Engine.
Manages global, tenant, and department settings (AI Models, Matching Weights, Hiring Rules, Regional Settings).
"""

from typing import Any, Dict, List, Optional
from app.admin.schemas.admin_models import ConfigurationEntry
from core.logging import get_logger

logger = get_logger("configuration_engine")


class ConfigurationEngine:
    """Enterprise Configuration Management Engine."""

    def __init__(self) -> None:
        self._configs: Dict[str, ConfigurationEntry] = {}
        self._seed_default_configs()

    def _seed_default_configs(self) -> None:
        defaults = [
            ("ai.model_name", "llama3:8b", "global"),
            ("matching.publication_weight", 0.35, "global"),
            ("matching.experience_weight", 0.30, "global"),
            ("matching.education_weight", 0.25, "global"),
            ("matching.grant_weight", 0.10, "global"),
            ("workflow.committee_approval_required", True, "global"),
            ("regional.timezone", "Asia/Kolkata", "global"),
            ("regional.date_format", "DD/MM/YYYY", "global"),
        ]
        for key, val, scope in defaults:
            c = ConfigurationEntry(key=key, value=val, scope=scope)
            self._configs[key] = c

        logger.info("Seeded default system configurations", count=len(self._configs))

    def get_setting(self, key: str, default: Any = None) -> Any:
        config = self._configs.get(key)
        return config.value if config else default

    def set_setting(self, key: str, value: Any, updated_by: str = "system", scope: str = "global") -> ConfigurationEntry:
        config = ConfigurationEntry(key=key, value=value, scope=scope, updated_by=updated_by)
        self._configs[key] = config
        logger.info("Configuration updated", key=key, value=value, updated_by=updated_by)
        return config

    def list_settings(self) -> List[ConfigurationEntry]:
        return list(self._configs.values())
