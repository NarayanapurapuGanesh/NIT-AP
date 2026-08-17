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

    # Session Defaults
    DEFAULT_MAX_TURNS: int = int(os.getenv("INTERACTION_MAX_TURNS", "12"))
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("INTERACTION_TIMEOUT_MINUTES", "45"))
    DEFAULT_PERSONA: str = os.getenv("INTERACTION_DEFAULT_PERSONA", "Beginner")

    # AI Parameters
    STUDENT_TEMPERATURE: float = float(os.getenv("STUDENT_TEMPERATURE", "0.7"))
    EVALUATOR_TEMPERATURE: float = float(os.getenv("EVALUATOR_TEMPERATURE", "0.1"))
    MAX_TOKENS_STUDENT: int = int(os.getenv("MAX_TOKENS_STUDENT", "512"))
    MAX_TOKENS_EVALUATOR: int = int(os.getenv("MAX_TOKENS_EVALUATOR", "1024"))

    # Features
    ENABLE_RAG: bool = os.getenv("INTERACTION_ENABLE_RAG", "false").lower() == "true"
    ENABLE_STREAMING: bool = os.getenv("INTERACTION_ENABLE_STREAMING", "false").lower() == "true"
    ENABLE_AUDIO: bool = os.getenv("INTERACTION_ENABLE_AUDIO", "false").lower() == "true"
    MODE: str = os.getenv("INTERACTION_MODE", "assessment")  # assessment | practice

    # CORS
    FRONTEND_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3002",
    ]


settings = Settings()
