import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_CONFIGURED = False


def setup_logger(log_dir=None, level=logging.INFO):
    """Configure the 'wordhumanizer' logger once (file + console) and return it."""
    global _CONFIGURED
    logger = logging.getLogger("wordhumanizer")
    if _CONFIGURED:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    if log_dir is None:
        log_dir = Path(__file__).resolve().parent.parent / "logs"
    try:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            Path(log_dir) / "application.log", maxBytes=5_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        pass  # read-only location: console logging only

    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    console.setFormatter(formatter)
    logger.addHandler(console)

    _CONFIGURED = True
    return logger


def get_logger(name):
    return logging.getLogger(f"wordhumanizer.{name}")
