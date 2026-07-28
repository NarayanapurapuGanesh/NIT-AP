from pathlib import Path
from pydantic_settings import BaseSettings


class StorageSettings(BaseSettings):
    temp_dir: str = "temp"
    output_dir: str = "output"
    logs_dir: str = "logs"


class WhisperSettings(BaseSettings):
    model_size: str = "small"
    device: str = "cuda"
    compute_type: str = "auto"


class Settings(BaseSettings):
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    host: str = "0.0.0.0"
    port: int = 8005
    log_level: str = "INFO"
    storage: StorageSettings = StorageSettings()
    whisper: WhisperSettings = WhisperSettings()


settings = Settings()
