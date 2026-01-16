"""
============================================================================
Ash: Crisis Detection Ecosystem API
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Listen   → Maintain vigilant presence across all community spaces
    Detect   → Identify mental health crisis patterns through comprehensive analysis
    Connect  → Bridge community members to timely support and intervention
    Protect  → Safeguard our LGBTQIA+ chosen family through early crisis response

============================================================================
Logging Configuration Manager - Colorized, Human-Readable Logging
----------------------------------------------------------------------------
FILE VERSION: v5.0-1-1.2-1
LAST MODIFIED: 2026-01-15
PHASE: Phase 1 - Ecosystem Health API
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# =============================================================================
# ANSI Color Codes for Human-Readable Logs
# =============================================================================
class Colors:
    """ANSI escape codes for colorized console output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Log level colors
    DEBUG = "\033[36m"      # Cyan
    INFO = "\033[32m"       # Green
    WARNING = "\033[33m"    # Yellow
    ERROR = "\033[31m"      # Red
    CRITICAL = "\033[35m"   # Magenta

    # Component colors
    TIMESTAMP = "\033[90m"  # Gray
    NAME = "\033[94m"       # Light blue
    MESSAGE = "\033[97m"    # White


# =============================================================================
# Custom Formatter for Human-Readable Logs
# =============================================================================
class HumanReadableFormatter(logging.Formatter):
    """
    Custom formatter that produces colorized, human-readable log output.

    Format: [TIMESTAMP] LEVEL    | logger_name | message
    """

    LEVEL_COLORS = {
        logging.DEBUG: Colors.DEBUG,
        logging.INFO: Colors.INFO,
        logging.WARNING: Colors.WARNING,
        logging.ERROR: Colors.ERROR,
        logging.CRITICAL: Colors.CRITICAL,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors and alignment."""
        # Get color for this level
        level_color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Pad level name for alignment
        level_name = record.levelname.ljust(8)

        # Truncate logger name if too long
        logger_name = record.name
        if len(logger_name) > 25:
            logger_name = "..." + logger_name[-22:]

        # Build the formatted message
        formatted = (
            f"{Colors.TIMESTAMP}[{timestamp}]{Colors.RESET} "
            f"{level_color}{Colors.BOLD}{level_name}{Colors.RESET} "
            f"{Colors.DIM}|{Colors.RESET} "
            f"{Colors.NAME}{logger_name.ljust(25)}{Colors.RESET} "
            f"{Colors.DIM}|{Colors.RESET} "
            f"{Colors.MESSAGE}{record.getMessage()}{Colors.RESET}"
        )

        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{Colors.ERROR}{self.formatException(record.exc_info)}{Colors.RESET}"

        return formatted


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        import json

        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


# =============================================================================
# Logging Configuration Manager
# =============================================================================
class LoggingConfigManager:
    """
    Manages logging configuration with colorized human-readable output.

    Features:
        - Colorized console output for development
        - JSON format option for production log aggregation
        - File logging with rotation support
        - Per-module log level configuration
    """

    def __init__(
        self,
        level: str = "INFO",
        log_format: str = "human",
        log_file: Optional[str] = None,
        console_enabled: bool = True,
        app_name: str = "ash",
    ):
        """
        Initialize the logging configuration manager.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_format: Output format ('human' or 'json')
            log_file: Optional file path for log output
            console_enabled: Whether to output logs to console
            app_name: Application name for the root logger
        """
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.log_format = log_format.lower()
        self.log_file = log_file
        self.console_enabled = console_enabled
        self.app_name = app_name

        # Configure the root logger
        self._configure_logging()

    def _configure_logging(self) -> None:
        """Configure the logging system."""
        # Get the root logger for our application
        root_logger = logging.getLogger(self.app_name)
        root_logger.setLevel(self.level)

        # Remove any existing handlers
        root_logger.handlers.clear()

        # Select formatter based on format setting
        if self.log_format == "json":
            formatter = JsonFormatter()
        else:
            formatter = HumanReadableFormatter()

        # Add console handler if enabled
        if self.console_enabled:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        # Add file handler if configured
        if self.log_file:
            # Ensure the log directory exists
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(self.level)
            # Always use JSON for file logging (easier to parse)
            file_handler.setFormatter(JsonFormatter())
            root_logger.addHandler(file_handler)

        # Prevent propagation to avoid duplicate logs
        root_logger.propagate = False

        # Also configure uvicorn loggers to use our format
        for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
            uvicorn_logger = logging.getLogger(logger_name)
            uvicorn_logger.handlers.clear()
            if self.console_enabled:
                uvicorn_logger.addHandler(console_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance with the specified name.

        Args:
            name: Logger name (typically __name__ of the calling module)

        Returns:
            Configured logger instance
        """
        # Create a child logger under our app name
        if not name.startswith(self.app_name):
            name = f"{self.app_name}.{name}"

        return logging.getLogger(name)

    def set_level(self, level: str) -> None:
        """
        Update the logging level at runtime.

        Args:
            level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.level = getattr(logging, level.upper(), logging.INFO)
        root_logger = logging.getLogger(self.app_name)
        root_logger.setLevel(self.level)

        for handler in root_logger.handlers:
            handler.setLevel(self.level)


# =============================================================================
# Factory Function (Clean Architecture Rule #1)
# =============================================================================
def create_logging_manager(
    level: str = "INFO",
    log_format: str = "human",
    log_file: Optional[str] = None,
    console_enabled: bool = True,
    app_name: str = "ash",
) -> LoggingConfigManager:
    """
    Factory function to create a LoggingConfigManager instance.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format ('human' or 'json')
        log_file: Optional file path for log output
        console_enabled: Whether to output logs to console
        app_name: Application name for the root logger

    Returns:
        Configured LoggingConfigManager instance
    """
    return LoggingConfigManager(
        level=level,
        log_format=log_format,
        log_file=log_file,
        console_enabled=console_enabled,
        app_name=app_name,
    )


__all__ = [
    "LoggingConfigManager",
    "create_logging_manager",
    "Colors",
    "HumanReadableFormatter",
    "JsonFormatter",
]
