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
Logging Configuration Manager - Charter v5.2 Compliant Colorized Logging
----------------------------------------------------------------------------
FILE VERSION: v5.0-6-1.0-3
LAST MODIFIED: 2026-01-17
PHASE: Phase 6 - Logging Colorization Enforcement
CLEAN ARCHITECTURE: Compliant
FILE RENAME: logging_manager.py → logging_config_manager.py (ecosystem consistency)
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================

RESPONSIBILITIES:
- Configure colorized console logging per Charter v5.2 Rule #9
- Support JSON format for production log aggregation
- Provide consistent log formatting across all Ash (Core) modules
- Enable log level filtering via configuration
- Create child loggers for component isolation
- Custom SUCCESS level for positive confirmations
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Module version
__version__ = "v5.0-6-1.1-1"


# =============================================================================
# Custom SUCCESS Log Level (between INFO and WARNING)
# =============================================================================
SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


def _success(self, message, *args, **kwargs):
    """Log a SUCCESS level message."""
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)


# Add success method to Logger class
logging.Logger.success = _success


# =============================================================================
# ANSI Color Codes - Charter v5.2 Standard
# =============================================================================
class Colors:
    """
    ANSI escape codes for colorized console output.

    Charter v5.2 Rule #9 Compliant Color Scheme:
    - CRITICAL: Bright Red Bold - System failures, data loss risks
    - ERROR:    Bright Red      - Exceptions, failed operations
    - WARNING:  Bright Yellow   - Degraded state, potential issues
    - INFO:     Bright Cyan     - Normal operations, status updates
    - DEBUG:    Gray            - Diagnostic details, verbose output
    - SUCCESS:  Bright Green    - Successful completions
    """

    # Reset
    RESET = "\033[0m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Charter v5.2 Standard Log Level Colors
    CRITICAL = "\033[1;91m"  # Bright Red Bold
    ERROR = "\033[91m"  # Bright Red
    WARNING = "\033[93m"  # Bright Yellow
    INFO = "\033[96m"  # Bright Cyan
    DEBUG = "\033[90m"  # Gray
    SUCCESS = "\033[92m"  # Bright Green

    # Additional colors for formatting
    TIMESTAMP = "\033[90m"  # Gray
    LOGGER_NAME = "\033[94m"  # Bright Blue
    MESSAGE = "\033[97m"  # Bright White


# =============================================================================
# Colorized Formatter - Charter v5.2 Compliant
# =============================================================================
class HumanReadableFormatter(logging.Formatter):
    """
    Custom formatter with Charter v5.2 compliant colorization.

    Format: [TIMESTAMP] LEVEL    | logger_name | message
    """

    LEVEL_COLORS = {
        logging.CRITICAL: Colors.CRITICAL,
        logging.ERROR: Colors.ERROR,
        logging.WARNING: Colors.WARNING,
        logging.INFO: Colors.INFO,
        logging.DEBUG: Colors.DEBUG,
        SUCCESS_LEVEL: Colors.SUCCESS,
    }

    LEVEL_SYMBOLS = {
        logging.CRITICAL: "🚨",
        logging.ERROR: "❌",
        logging.WARNING: "⚠️ ",
        logging.INFO: "ℹ️ ",
        logging.DEBUG: "🔍",
        SUCCESS_LEVEL: "✅",
    }

    def __init__(
        self,
        use_colors: bool = True,
        use_symbols: bool = True,
        datefmt: str = "%Y-%m-%d %H:%M:%S",
    ):
        """
        Initialize the colorized formatter.

        Args:
            use_colors: Whether to use ANSI color codes
            use_symbols: Whether to use emoji symbols
            datefmt: Date format string
        """
        super().__init__(datefmt=datefmt)
        self.use_colors = use_colors
        self.use_symbols = use_symbols

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors and alignment."""
        # Get color for this level
        level_color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)
        symbol = self.LEVEL_SYMBOLS.get(record.levelno, "") if self.use_symbols else ""

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime(self.datefmt)

        # Pad level name for alignment
        level_name = record.levelname.ljust(8)

        # Truncate logger name if too long
        logger_name = record.name
        if len(logger_name) > 25:
            logger_name = "..." + logger_name[-22:]
        logger_name = logger_name.ljust(25)

        # Get the message
        message = record.getMessage()

        # Build formatted output
        if self.use_colors:
            formatted = (
                f"{Colors.TIMESTAMP}[{timestamp}]{Colors.RESET} "
                f"{level_color}{level_name}{Colors.RESET} "
                f"{Colors.DIM}|{Colors.RESET} "
                f"{Colors.LOGGER_NAME}{logger_name}{Colors.RESET} "
                f"{Colors.DIM}|{Colors.RESET} "
                f"{symbol} {level_color}{message}{Colors.RESET}"
            )
        else:
            formatted = (
                f"[{timestamp}] {level_name} | {logger_name} | {symbol} {message}"
            )

        # Add exception info if present
        if record.exc_info:
            exc_text = self.formatException(record.exc_info)
            if self.use_colors:
                formatted += f"\n{Colors.ERROR}{exc_text}{Colors.RESET}"
            else:
                formatted += f"\n{exc_text}"

        return formatted


# =============================================================================
# JSON Formatter for Production
# =============================================================================
class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging in production."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        import json

        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
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
    Manages logging configuration with Charter v5.2 compliant colorization.

    Features:
        - Colorized console output (human format) per Charter v5.2 Rule #9
        - JSON format for production log aggregation
        - Custom SUCCESS level for positive confirmations
        - File logging with JSON format
        - Per-module logger creation

    Example:
        >>> logging_manager = create_logging_manager()
        >>> logger = logging_manager.get_logger("my_module")
        >>> logger.info("Ecosystem health check starting")
        >>> logger.success("All components healthy")
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
        self._configured_loggers: Dict[str, logging.Logger] = {}

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
            # Check for forced color output (useful for Docker containers)
            # Set FORCE_COLOR=1 in environment to enable colors without TTY
            force_color = os.environ.get("FORCE_COLOR", "").lower() in (
                "1",
                "true",
                "yes",
            )
            use_colors = force_color or (
                hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
            )
            formatter = HumanReadableFormatter(use_colors=use_colors, use_symbols=True)

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

            file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
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
        if name in self._configured_loggers:
            return self._configured_loggers[name]

        # Create a child logger under our app name
        if not name.startswith(self.app_name):
            name = f"{self.app_name}.{name}"

        logger = logging.getLogger(name)
        self._configured_loggers[name] = logger
        return logger

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

    def get_level(self) -> str:
        """Get current log level name."""
        return logging.getLevelName(self.level)

    def get_format(self) -> str:
        """Get current log format."""
        return self.log_format


# =============================================================================
# Factory Function (Clean Architecture Rule #1)
# =============================================================================
def create_logging_config_manager(
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


# Backward compatibility alias
create_logging_manager = create_logging_config_manager


__all__ = [
    "LoggingConfigManager",
    "create_logging_config_manager",
    "create_logging_manager",  # Backward compatibility
    "Colors",
    "HumanReadableFormatter",
    "JsonFormatter",
    "SUCCESS_LEVEL",
]
