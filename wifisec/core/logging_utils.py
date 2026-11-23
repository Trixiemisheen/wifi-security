"""Logging helper for the suite."""
import logging

from wifisec.core.config import LOG_FILE


def get_logger(name: str = "wifisec") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        try:
            handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        except OSError:
            handler = logging.NullHandler()
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_event(message: str) -> None:
    get_logger().info(message)