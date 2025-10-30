"""Logging configuration for colorscheme orchestrator."""

import logging
import sys
from pathlib import Path


def setup_logging(
    debug: bool = False,
    log_file: Path | None = None,
) -> logging.Logger:
    """Setup logging for the orchestrator.

    Args:
        debug: Enable debug logging
        log_file: Optional log file path

    Returns:
        logging.Logger: Configured logger
    """
    # Determine log level
    level = logging.DEBUG if debug else logging.INFO

    # Get root logger for colorscheme-orchestrator
    logger = logging.getLogger("colorscheme-orchestrator")
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler if requested
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (defaults to colorscheme-orchestrator)

    Returns:
        logging.Logger: Logger instance
    """
    if name:
        return logging.getLogger(f"colorscheme-orchestrator.{name}")
    return logging.getLogger("colorscheme-orchestrator")
