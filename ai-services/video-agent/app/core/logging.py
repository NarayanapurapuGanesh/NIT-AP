import sys
from loguru import logger
from app.config.settings import settings
from app.utils.file_utils import ensure_directory


def setup_logging() -> None:
    """Configures Loguru logger sinks for stdout and file logging."""
    logger.remove()

    # Log to stdout
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        enqueue=True,
    )

    # Log to file
    log_dir = ensure_directory(settings.base_dir / settings.storage.logs_dir)
    log_file = log_dir / "video_agent.log"

    logger.add(
        str(log_file),
        rotation="10 MB",
        retention="14 days",
        level="DEBUG",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )

    logger.info(f"Logging initialized. Writing logs to {log_file}")
