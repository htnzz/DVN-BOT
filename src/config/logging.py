import sys
from pathlib import Path

from loguru import logger


def setup_logging() -> None:
    project_root = Path(__file__).resolve().parents[2]
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        colorize=True,
        level="INFO",
        enqueue=True,
        backtrace=True,
        diagnose=False,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
            "- <level>{message}</level>"
        ),
    )

    logger.add(
        logs_dir / "{time:YYYY-MM-DD}.log",
        level="INFO",
        enqueue=True,
        backtrace=True,
        diagnose=False,
        rotation="00:00",
        retention="7 days",
        compression=None,
        encoding="utf-8",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{name}:{function}:{line} - {message}"
        ),
    )
