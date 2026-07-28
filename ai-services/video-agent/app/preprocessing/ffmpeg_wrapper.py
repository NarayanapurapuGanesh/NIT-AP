import subprocess
from typing import List
from loguru import logger
from app.core.exceptions import PreprocessingError


class FFmpegWrapper:
    """Wrapper executing FFmpeg CLI sub-commands safely."""

    def run_command(self, args: List[str], description: str = "FFmpeg command") -> str:
        cmd = ["ffmpeg"] + args
        logger.debug(f"Executing FFmpeg [{description}]: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return res.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg [{description}] failed: {e.stderr}")
            raise PreprocessingError(f"FFmpeg error during {description}: {e.stderr}") from e
