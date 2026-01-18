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
Unified Configuration Manager - JSON Config with Environment Overrides
----------------------------------------------------------------------------
FILE VERSION: v5.0-6-1.0-1
LAST MODIFIED: 2026-01-18
PHASE: Phase 6 - Logging Colorization
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.managers.logging_config_manager import create_logging_config_manager, LoggingConfigManager


# =============================================================================
# Configuration Manager
# =============================================================================
class ConfigManager:
    """
    Unified configuration manager following Clean Architecture principles.

    Features:
        - Loads JSON configuration from default.json
        - Environment variables override JSON defaults (Rule #4)
        - Resilient validation with smart fallbacks (Rule #5)
        - Type coercion for environment variable strings
    """

    # Regex pattern to detect environment variable placeholders
    ENV_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")

    def __init__(
        self,
        config_path: Optional[str] = None,
        logger: Optional[LoggingConfigManager] = None,
    ):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the JSON configuration file
            logger: Optional logging manager instance
        """
        # Set up logging first (bootstrap with defaults)
        self._logger = logger or create_logging_config_manager()
        self._log = self._logger.get_logger("config_manager")

        # Determine config file path
        if config_path is None:
            # Default to src/config/default.json relative to this file
            config_path = Path(__file__).parent.parent / "config" / "default.json"
        else:
            config_path = Path(config_path)

        self._config_path = config_path
        self._raw_config: Dict[str, Any] = {}
        self._resolved_config: Dict[str, Any] = {}

        # Load configuration
        self._load_config()

    def _load_config(self) -> None:
        """Load and resolve the JSON configuration file."""
        try:
            if not self._config_path.exists():
                self._log.warning(
                    f"⚠️  Config file not found: {self._config_path}, using defaults"
                )
                self._raw_config = {}
                self._resolved_config = {}
                return

            with open(self._config_path, "r", encoding="utf-8") as f:
                self._raw_config = json.load(f)

            self._log.info(f"✅ Loaded configuration from {self._config_path}")

            # Resolve environment variable placeholders
            self._resolved_config = self._resolve_config(self._raw_config)

        except json.JSONDecodeError as e:
            self._log.error(f"❌ Invalid JSON in config file: {e}")
            self._raw_config = {}
            self._resolved_config = {}
        except Exception as e:
            self._log.error(f"❌ Failed to load config: {e}")
            self._raw_config = {}
            self._resolved_config = {}

    def _resolve_config(self, config: Any, path: str = "") -> Any:
        """
        Recursively resolve environment variable placeholders in config.

        Args:
            config: Configuration value (dict, list, or scalar)
            path: Current path in the config tree (for logging)

        Returns:
            Resolved configuration value
        """
        if isinstance(config, dict):
            resolved = {}
            for key, value in config.items():
                # Skip metadata and validation sections
                if key in ("_metadata", "validation", "defaults", "description"):
                    resolved[key] = value
                    continue

                new_path = f"{path}.{key}" if path else key
                resolved[key] = self._resolve_config(value, new_path)
            return resolved

        elif isinstance(config, list):
            return [
                self._resolve_config(item, f"{path}[{i}]")
                for i, item in enumerate(config)
            ]

        elif isinstance(config, str):
            return self._resolve_env_var(config, path)

        else:
            return config

    def _resolve_env_var(self, value: str, path: str) -> Any:
        """
        Resolve an environment variable placeholder.

        Args:
            value: String potentially containing ${ENV_VAR} pattern
            path: Config path for logging/fallback lookup

        Returns:
            Resolved value (from env var or defaults)
        """
        match = self.ENV_VAR_PATTERN.match(value)
        if not match:
            return value

        env_var_name = match.group(1)
        env_value = os.environ.get(env_var_name)

        if env_value is not None:
            # Environment variable is set, use it
            self._log.debug(f"🔧 Using env override for {path}: ${{{env_var_name}}}")
            return self._coerce_type(env_value, path)

        # Fall back to default value from config
        default_value = self._get_default_for_path(path)
        if default_value is not None:
            self._log.debug(f"📋 Using default for {path}: {default_value}")
            return default_value

        # No default found, return the placeholder as-is (will likely fail validation)
        self._log.warning(f"⚠️  No value for {env_var_name} and no default at {path}")
        return value

    def _get_default_for_path(self, path: str) -> Any:
        """
        Get the default value for a configuration path.

        Args:
            path: Dot-separated path like "server.host"

        Returns:
            Default value if found, None otherwise
        """
        parts = path.split(".")
        if len(parts) < 2:
            return None

        # Navigate to the section containing 'defaults'
        section = self._raw_config
        for part in parts[:-1]:
            if isinstance(section, dict) and part in section:
                section = section[part]
            else:
                return None

        # Look for 'defaults' in this section
        if isinstance(section, dict) and "defaults" in section:
            defaults = section["defaults"]
            key = parts[-1]
            if isinstance(defaults, dict) and key in defaults:
                return defaults[key]

        return None

    def _coerce_type(self, value: str, path: str) -> Any:
        """
        Coerce a string environment variable to the appropriate type.

        Args:
            value: String value from environment
            path: Config path for type inference

        Returns:
            Type-coerced value
        """
        # Check for boolean
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        if value.lower() in ("false", "no", "0", "off"):
            return False

        # Check for integer
        try:
            return int(value)
        except ValueError:
            pass

        # Check for float
        try:
            return float(value)
        except ValueError:
            pass

        # Check for JSON (lists, dicts)
        if value.startswith(("[", "{")):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass

        # Return as string
        return value

    def get(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot-separated path.

        Args:
            path: Dot-separated path like "server.host"
            default: Default value if path not found

        Returns:
            Configuration value or default
        """
        parts = path.split(".")
        value = self._resolved_config

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.

        Args:
            section: Section name (e.g., "server", "logging")

        Returns:
            Section dictionary or empty dict
        """
        return self._resolved_config.get(section, {})

    def get_component_config(self, component: str) -> Dict[str, Any]:
        """
        Get configuration for a specific ecosystem component.

        Args:
            component: Component key (e.g., "ash_bot", "ash_nlp")

        Returns:
            Component configuration dictionary
        """
        components = self._resolved_config.get("components", {})
        return components.get(component, {})

    def get_all_components(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all component configurations.

        Returns:
            Dictionary of all component configurations
        """
        return self._resolved_config.get("components", {})

    def get_connection_checks(self) -> List[Dict[str, Any]]:
        """
        Get the list of connection checks to perform.

        Returns:
            List of connection check configurations
        """
        connections = self._resolved_config.get("connections", {})
        return connections.get("checks", [])

    @property
    def server_host(self) -> str:
        """Get the server host address."""
        return self.get("server.host", "0.0.0.0")

    @property
    def server_port(self) -> int:
        """Get the server port."""
        return self.get("server.port", 30887)

    @property
    def environment(self) -> str:
        """Get the environment name."""
        return self.get("server.environment", "production")

    @property
    def log_level(self) -> str:
        """Get the logging level."""
        return self.get("logging.level", "INFO")

    @property
    def log_format(self) -> str:
        """Get the logging format."""
        return self.get("logging.format", "human")

    @property
    def log_file(self) -> Optional[str]:
        """Get the log file path."""
        return self.get("logging.file")

    @property
    def log_console(self) -> bool:
        """Get whether console logging is enabled."""
        return self.get("logging.console", True)

    @property
    def check_timeout_ms(self) -> int:
        """Get the health check timeout in milliseconds."""
        return self.get("ecosystem.check_timeout_ms", 5000)

    @property
    def alerting_enabled(self) -> bool:
        """Get whether alerting is enabled."""
        return self.get("alerting.enabled", True)

    @property
    def alerting_check_interval_seconds(self) -> int:
        """Get the alerting check interval in seconds."""
        return self.get("alerting.check_interval_seconds", 60)

    @property
    def alerting_cooldown_seconds(self) -> int:
        """Get the alerting cooldown in seconds (minimum time between alerts for same entity)."""
        return self.get("alerting.cooldown_seconds", 300)

    @property
    def alerting_on_degraded(self) -> bool:
        """Get whether to alert when components become degraded."""
        return self.get("alerting.alert_on_degraded", True)

    @property
    def alerting_on_recovery(self) -> bool:
        """Get whether to alert when components recover."""
        return self.get("alerting.alert_on_recovery", True)

    @property
    def alerting_on_connection_issues(self) -> bool:
        """Get whether to alert on inter-component connection issues."""
        return self.get("alerting.alert_on_connection_issues", True)

    # =========================================================================
    # Metrics Configuration (Phase 5)
    # =========================================================================
    @property
    def metrics_enabled(self) -> bool:
        """Get whether historical metrics collection is enabled."""
        return self.get("metrics.enabled", True)

    @property
    def metrics_db_path(self) -> str:
        """Get the SQLite database path for metrics storage."""
        return self.get("metrics.db_path", "/app/data/metrics.db")

    @property
    def metrics_retention_snapshots_days(self) -> int:
        """Get the retention period for raw health snapshots (days)."""
        return self.get("metrics.retention_snapshots_days", 7)

    @property
    def metrics_retention_incidents_days(self) -> int:
        """Get the retention period for incident records (days)."""
        return self.get("metrics.retention_incidents_days", 90)

    @property
    def metrics_retention_aggregates_days(self) -> int:
        """Get the retention period for daily aggregates (days)."""
        return self.get("metrics.retention_aggregates_days", 365)

    @property
    def metrics_maintenance_hour(self) -> int:
        """Get the hour (UTC) when daily maintenance should run."""
        return self.get("metrics.maintenance_hour", 3)


# =============================================================================
# Factory Function (Clean Architecture Rule #1)
# =============================================================================
def create_config_manager(
    config_path: Optional[str] = None,
    logger: Optional[LoggingConfigManager] = None,
) -> ConfigManager:
    """
    Factory function to create a ConfigManager instance.

    Args:
        config_path: Path to the JSON configuration file
        logger: Optional logging manager instance

    Returns:
        Configured ConfigManager instance
    """
    return ConfigManager(config_path=config_path, logger=logger)


__all__ = ["ConfigManager", "create_config_manager"]
