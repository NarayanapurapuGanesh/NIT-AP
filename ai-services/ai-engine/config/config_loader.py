import yaml
import os
import logging

logger = logging.getLogger(__name__)

class ConfigLoader:
    _instance = None

    def __new__(cls, config_path: str = "config/gpu.yaml"):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._config = {}
            cls._instance._load(config_path)
        return cls._instance

    def _load(self, config_path: str):
        if not os.path.exists(config_path):
            logger.warning(f"Config file {config_path} not found. Using defaults.")
            return

        with open(config_path, 'r') as f:
            try:
                self._config = yaml.safe_load(f) or {}
                logger.info(f"Loaded config from {config_path}")
            except Exception as e:
                logger.error(f"Failed to parse {config_path}: {e}")

    @property
    def gpu_config(self):
        return self._config.get('gpu', {})

    @property
    def performance_config(self):
        return self._config.get('performance', {})

def get_config():
    return ConfigLoader()
