"""
Loguru configuration.

Why Loguru over stdlib logging: far less boilerplate for structured,
readable output, and trivial to add JSON sink later for production
log aggregation (e.g., shipping to Datadog/ELK).
"""

import sys

from loguru import logger

from postgres_mcp.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    logger.remove()  # remove Loguru's default handler
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
            "- <level>{message}</level>"
        ),
    )