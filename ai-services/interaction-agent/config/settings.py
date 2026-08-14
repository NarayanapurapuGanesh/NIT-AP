import os

class Settings:
    """Configuration for the Interaction Agent service."""

    # Service
    HOST: str = os.getenv("INTERACTION_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("INTERACTION_PORT", "8020"))

    # Ollama
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    STUDENT_MODEL: str = os.getenv("STUDENT_MODEL", "llama3.2:3b")
    EVALUATOR_MODEL: str = os.getenv("EVALUATOR_MODEL", "qwen2.5:3b")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://:redis_secure_password_123!@localhost:6379/1")

    # Session Defaults
    DEFAULT_MAX_TURNS: int = int(os.getenv("DEFAULT_MAX_TURNS", "20"))
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "45"))

    # AI Parameters
    STUDENT_TEMPERATURE: float = float(os.getenv("STUDENT_TEMPERATURE", "0.7"))
    EVALUATOR_TEMPERATURE: float = float(os.getenv("EVALUATOR_TEMPERATURE", "0.1"))
    MAX_TOKENS_STUDENT: int = int(os.getenv("MAX_TOKENS_STUDENT", "512"))
    MAX_TOKENS_EVALUATOR: int = int(os.getenv("MAX_TOKENS_EVALUATOR", "1024"))


settings = Settings()
