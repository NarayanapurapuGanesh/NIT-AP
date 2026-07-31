import os
import yaml
import subprocess
from loguru import logger
from fastapi import HTTPException, status
from pathlib import Path

class AIModelService:
    """Service to manage AI models using a centralized YAML configuration."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.models_config = {}
        
    def loadConfiguration(self):
        """Loads the configuration from ai-models.yaml."""
        if not self.config_path.exists():
            logger.error(f"Configuration file not found at {self.config_path}")
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")
            
        try:
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
                self.models_config = config.get("models", {})
                logger.info("Successfully loaded ai-models.yaml")
        except Exception as e:
            logger.error(f"Failed to parse configuration file: {e}")
            raise
            
    def reloadConfiguration(self):
        """Reloads the configuration."""
        self.loadConfiguration()
        
    def getModel(self, agent_name: str) -> str:
        """Retrieves the assigned model for a specific agent."""
        agent_config = self.models_config.get(agent_name)
        if not agent_config or "primary" not in agent_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No primary model configured for agent '{agent_name}'"
            )
        return agent_config["primary"]
        
    def list_ollama_models(self) -> list[str]:
        """Lists available models from local Ollama instance."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True, text=True, check=True
            )
            lines = result.stdout.strip().split("\n")[1:] # Skip header
            models = []
            for line in lines:
                if line:
                    parts = line.split()
                    if parts:
                        models.append(parts[0])
            return models
        except Exception as e:
            logger.error(f"Failed to fetch ollama list: {e}")
            return []

    def validateModelExists(self, model_name: str) -> str:
        """Validates that the specified model is pulled in Ollama."""
        available_models = self.list_ollama_models()
        if model_name not in available_models:
            # Check if user forgot the :latest tag
            if f"{model_name}:latest" in available_models:
                return f"{model_name}:latest"
            
            error_msg = f"Model '{model_name}' is not found in local Ollama. Please run `ollama pull {model_name}`."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        return model_name
        
    def validate_all_startup_models(self):
        """Validates all configured models exist at startup and logs mappings."""
        logger.info("Validating configured AI models...")
        for agent_name, agent_config in self.models_config.items():
            model = agent_config.get("primary")
            if model:
                try:
                    resolved_model = self.validateModelExists(model)
                    logger.info(f"{agent_name.capitalize()} Agent \u2192 {resolved_model}")
                except Exception as e:
                    logger.error(f"Startup validation failed for {agent_name} agent: {e}")
                    raise
