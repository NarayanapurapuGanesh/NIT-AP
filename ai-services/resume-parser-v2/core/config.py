"""
Central Configuration System using pydantic-settings v2.
Supports Development, Testing, and Production environment configurations seamlessly.
"""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.constants import EnvironmentOption, LogLevelOption


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # Core Application Attributes
    APP_NAME: str = Field(default="resume-parser-v2", description="Application identifier name")
    APP_ENV: EnvironmentOption = Field(
        default=EnvironmentOption.DEVELOPMENT, description="Execution environment mode"
    )
    DEBUG: bool = Field(default=True, description="Enable debug mode and verbose tracebacks")
    API_V1_STR: str = Field(default="/api/v1", description="Prefix for Version 1 API routes")
    SECRET_KEY: str = Field(
        default="secret_key_change_in_production_environment_32chars",
        description="Cryptographic secret key for signing tokens and hashes",
    )

    # Host & Server Execution Parameters
    HOST: str = Field(default="0.0.0.0", description="Bind host address")
    PORT: int = Field(default=8000, description="Port number to serve FastAPI app")
    WORKERS: int = Field(default=1, description="Number of process workers")

    # Security & CORS Settings
    ALLOWED_ORIGINS: Union[str, List[str]] = Field(
        default=["*"],
        description="Comma-separated or list of allowed CORS origins",
    )
    ALLOWED_HOSTS: Union[str, List[str]] = Field(
        default=["*"], description="Comma-separated or list of trusted host headers"
    )

    # Logging Controls
    LOG_LEVEL: LogLevelOption = Field(
        default=LogLevelOption.INFO, description="Minimum logging level verbosity"
    )
    LOG_JSON_FORMAT: bool = Field(
        default=False, description="Format logs as JSON lines for centralized logging ingestion"
    )

    # Infrastructure Integration Stubs (Lazy Loading Readiness)
    QDRANT_HOST: str = Field(default="localhost", description="Qdrant Vector Database Host")
    QDRANT_PORT: int = Field(default=6333, description="Qdrant Vector Database Port")
    MINIO_ENDPOINT: str = Field(default="localhost:9000", description="MinIO Object Storage Endpoint")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama API base URL")

    @field_validator("ALLOWED_ORIGINS", "ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_cors_and_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.strip() == "*":
                return ["*"]
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == EnvironmentOption.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == EnvironmentOption.PRODUCTION

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV == EnvironmentOption.TESTING


settings = Settings()
