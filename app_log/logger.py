import logging
from logging.handlers import RotatingFileHandler
from rich.logging import RichHandler
from pathlib import Path
from app.settings import settings


LOG_LEVEL = logging.DEBUG if settings.debug else logging.INFO
LOG_DIR = Path(settings.log_dir)
LOG_FILE = LOG_DIR / "agent.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(LOG_LEVEL)

    # File Handler (Persistent Logs)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
    )

    # Console Handler (Pretty Logs)
    console_handler = RichHandler(
        rich_tracebacks=True,
        show_time=False,
        show_level=True,
        show_path=False,
    )
    console_handler.setLevel(LOG_LEVEL)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.propagate = False
    return logger
