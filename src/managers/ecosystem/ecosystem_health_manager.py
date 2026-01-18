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
Ecosystem Health Manager - Aggregated Health Monitoring for Ash Components
----------------------------------------------------------------------------
FILE VERSION: v5.0-1-1.3-2
LAST MODIFIED: 2026-01-15
PHASE: Phase 1 - Ecosystem Health API
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx

from src.managers.config_manager import ConfigManager
from src.managers.logging_manager import LoggingConfigManager


# =============================================================================
# Status Enums and Data Classes
# =============================================================================
class ComponentStatus(str, Enum):
    """Status values for ecosystem components."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNREACHABLE = "unreachable"
    DISABLED = "disabled"


@dataclass
class ComponentHealth:
    """Health status for a single ecosystem component."""

    name: str
    status: ComponentStatus
    endpoint: str
    response_time_ms: Optional[float] = None
    version: Optional[str] = None
    uptime_seconds: Optional[int] = None
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConnectionHealth:
    """Health status for an inter-component connection."""

    name: str
    status: ComponentStatus
    latency_ms: Optional[float] = None
    error: Optional[str] = None
    critical: bool = False


@dataclass
class EcosystemHealth:
    """Aggregated health status for the entire ecosystem."""

    ecosystem: str = "ash"
    status: ComponentStatus = ComponentStatus.HEALTHY
    timestamp: str = ""
    summary: Dict[str, int] = field(default_factory=dict)
    components: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    connections: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "ecosystem": self.ecosystem,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "summary": self.summary,
            "components": self.components,
            "connections": self.connections,
            "meta": self.meta,
        }


# =============================================================================
# Ecosystem Health Manager
# =============================================================================
class EcosystemHealthManager:
    """
    Manages health monitoring for the entire Ash ecosystem.

    Features:
        - Parallel health checks to all components
        - Connection validation between components
        - Status aggregation and summary calculation
        - Resilient error handling (system doesn't crash on failures)
    """

    # Thresholds for status determination
    LATENCY_WARNING_MS = 1000  # Above this is "degraded"
    LATENCY_CRITICAL_MS = 5000  # Above this is "unhealthy"

    def __init__(
        self,
        config_manager: ConfigManager,
        logger: LoggingConfigManager,
    ):
        """
        Initialize the Ecosystem Health Manager.

        Args:
            config_manager: Configuration manager instance
            logger: Logging manager instance
        """
        self._config = config_manager
        self._logger = logger
        self._log = logger.get_logger("ecosystem_health")

        # HTTP client configuration
        self._timeout_seconds = self._config.check_timeout_ms / 1000.0

        self._log.info("✅ EcosystemHealthManager initialized")

    async def check_ecosystem_health(self) -> EcosystemHealth:
        """
        Perform a complete ecosystem health check.

        Returns:
            EcosystemHealth object with aggregated status
        """
        start_time = time.monotonic()
        self._log.info("🔍 Starting ecosystem health check...")

        # Initialize result
        result = EcosystemHealth(
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Check all components in parallel
        components = await self._check_all_components()
        result.components = {
            comp.name.lower().replace("-", "_"): self._component_to_dict(comp)
            for comp in components
        }

        # Check connections (only if source components are healthy)
        connections = await self._check_all_connections(components)
        result.connections = {
            conn.name: self._connection_to_dict(conn) for conn in connections
        }

        # Calculate summary
        result.summary = self._calculate_summary(components)

        # Determine overall status
        result.status = self._determine_overall_status(components, connections)

        # Add metadata
        check_duration_ms = (time.monotonic() - start_time) * 1000
        result.meta = {
            "check_duration_ms": round(check_duration_ms, 2),
            "timeout_ms": self._config.check_timeout_ms,
            "aggregator_version": "v5.0-1-1.3-2",
        }

        self._log.info(
            f"✅ Ecosystem health check complete: {result.status.value} "
            f"({check_duration_ms:.0f}ms)"
        )

        return result

    async def _check_all_components(self) -> List[ComponentHealth]:
        """
        Check health of all configured components in parallel.

        Returns:
            List of ComponentHealth objects
        """
        components_config = self._config.get_all_components()
        tasks = []

        for key, config in components_config.items():
            # Skip non-component entries (like "description", "defaults", etc.)
            if not isinstance(config, dict):
                continue

            # Skip metadata keys that might be dicts but aren't components
            if key in ("description", "defaults", "validation", "_metadata"):
                continue

            # Check if component is enabled
            enabled = config.get("enabled", config.get("defaults", {}).get("enabled", True))
            if not enabled:
                # Return a disabled status immediately
                tasks.append(self._create_disabled_component(key, config))
            else:
                tasks.append(self._check_component(key, config))

        return await asyncio.gather(*tasks)

    async def _create_disabled_component(
        self, key: str, config: Dict[str, Any]
    ) -> ComponentHealth:
        """Create a ComponentHealth for a disabled component."""
        name = config.get("name", key)
        health_url = config.get("health_url", config.get("defaults", {}).get("health_url", ""))

        return ComponentHealth(
            name=name,
            status=ComponentStatus.DISABLED,
            endpoint=health_url,
        )

    async def _check_component(
        self, key: str, config: Dict[str, Any]
    ) -> ComponentHealth:
        """
        Check the health of a single component.

        Args:
            key: Component key (e.g., "ash_bot")
            config: Component configuration dictionary

        Returns:
            ComponentHealth object
        """
        name = config.get("name", key)
        health_url = config.get("health_url", config.get("defaults", {}).get("health_url", ""))

        self._log.debug(f"🔍 Checking {name} at {health_url}")

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                start = time.monotonic()
                response = await client.get(health_url)
                response_time_ms = (time.monotonic() - start) * 1000

                if response.status_code == 200:
                    # Parse response for additional details
                    try:
                        data = response.json()
                    except Exception:
                        data = {}

                    # Determine status based on response and latency
                    status = self._determine_component_status(response_time_ms, data)

                    return ComponentHealth(
                        name=name,
                        status=status,
                        endpoint=health_url,
                        response_time_ms=round(response_time_ms, 2),
                        version=data.get("version"),
                        uptime_seconds=data.get("uptime_seconds"),
                        details=data,
                    )
                else:
                    # Non-200 response
                    return ComponentHealth(
                        name=name,
                        status=ComponentStatus.UNHEALTHY,
                        endpoint=health_url,
                        response_time_ms=round(response_time_ms, 2),
                        error=f"HTTP {response.status_code}",
                    )

        except httpx.TimeoutException:
            self._log.warning(f"⏱️  Timeout checking {name}")
            return ComponentHealth(
                name=name,
                status=ComponentStatus.UNREACHABLE,
                endpoint=health_url,
                error="Connection timeout",
            )
        except httpx.ConnectError as e:
            self._log.warning(f"🔌 Connection error for {name}: {e}")
            return ComponentHealth(
                name=name,
                status=ComponentStatus.UNREACHABLE,
                endpoint=health_url,
                error="Connection refused",
            )
        except Exception as e:
            self._log.error(f"❌ Error checking {name}: {e}")
            return ComponentHealth(
                name=name,
                status=ComponentStatus.UNREACHABLE,
                endpoint=health_url,
                error=str(e),
            )

    def _determine_component_status(
        self, response_time_ms: float, data: Dict[str, Any]
    ) -> ComponentStatus:
        """
        Determine component status based on response time and health data.

        Args:
            response_time_ms: Response time in milliseconds
            data: Parsed health response data

        Returns:
            ComponentStatus enum value
        """
        # Check if the component reports its own status
        reported_status = data.get("status", "").lower()
        if reported_status == "unhealthy":
            return ComponentStatus.UNHEALTHY
        if reported_status == "degraded":
            return ComponentStatus.DEGRADED

        # Check latency thresholds
        if response_time_ms > self.LATENCY_CRITICAL_MS:
            return ComponentStatus.UNHEALTHY
        if response_time_ms > self.LATENCY_WARNING_MS:
            return ComponentStatus.DEGRADED

        return ComponentStatus.HEALTHY

    async def _check_all_connections(
        self, components: List[ComponentHealth]
    ) -> List[ConnectionHealth]:
        """
        Check all configured inter-component connections.

        Args:
            components: List of component health results

        Returns:
            List of ConnectionHealth objects
        """
        connection_checks = self._config.get_connection_checks()
        results = []

        # Build a lookup of component health by key
        component_lookup = {
            comp.name.lower().replace("-", "_"): comp for comp in components
        }

        for check in connection_checks:
            source_key = check.get("source", "")
            target_key = check.get("target", "")
            check_name = check.get("name", f"{source_key} -> {target_key}")
            critical = check.get("critical", False)

            # Get source and target components
            source = component_lookup.get(source_key)
            target = component_lookup.get(target_key)

            # Skip if either endpoint is disabled or unreachable
            if not source or source.status in (
                ComponentStatus.DISABLED,
                ComponentStatus.UNREACHABLE,
            ):
                results.append(
                    ConnectionHealth(
                        name=check_name,
                        status=ComponentStatus.DISABLED,
                        critical=critical,
                        error=f"Source ({source_key}) unavailable",
                    )
                )
                continue

            if not target or target.status in (
                ComponentStatus.DISABLED,
                ComponentStatus.UNREACHABLE,
            ):
                results.append(
                    ConnectionHealth(
                        name=check_name,
                        status=ComponentStatus.DISABLED,
                        critical=critical,
                        error=f"Target ({target_key}) unavailable",
                    )
                )
                continue

            # Both endpoints are available - check connection
            # For now, we infer connection health from component health
            # Future: Could add actual connectivity tests
            combined_latency = (source.response_time_ms or 0) + (
                target.response_time_ms or 0
            )

            if combined_latency > self.LATENCY_CRITICAL_MS:
                status = ComponentStatus.UNHEALTHY
            elif combined_latency > self.LATENCY_WARNING_MS:
                status = ComponentStatus.DEGRADED
            else:
                status = ComponentStatus.HEALTHY

            results.append(
                ConnectionHealth(
                    name=check_name,
                    status=status,
                    latency_ms=round(combined_latency, 2),
                    critical=critical,
                )
            )

        return results

    def _calculate_summary(self, components: List[ComponentHealth]) -> Dict[str, int]:
        """
        Calculate summary counts by status.

        Args:
            components: List of component health results

        Returns:
            Dictionary with counts per status
        """
        summary = {
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0,
            "unreachable": 0,
            "disabled": 0,
        }

        for comp in components:
            summary[comp.status.value] += 1

        return summary

    def _determine_overall_status(
        self, components: List[ComponentHealth], connections: List[ConnectionHealth]
    ) -> ComponentStatus:
        """
        Determine the overall ecosystem status.

        Args:
            components: List of component health results
            connections: List of connection health results

        Returns:
            Overall ecosystem status
        """
        # Check for any unreachable or unhealthy components
        has_unreachable = any(
            c.status == ComponentStatus.UNREACHABLE for c in components
        )
        has_unhealthy = any(c.status == ComponentStatus.UNHEALTHY for c in components)
        has_degraded = any(c.status == ComponentStatus.DEGRADED for c in components)

        # Check for critical connection failures
        critical_connection_failed = any(
            conn.critical
            and conn.status in (ComponentStatus.UNHEALTHY, ComponentStatus.UNREACHABLE)
            for conn in connections
        )

        if has_unreachable or has_unhealthy or critical_connection_failed:
            return ComponentStatus.UNHEALTHY
        if has_degraded:
            return ComponentStatus.DEGRADED

        return ComponentStatus.HEALTHY

    def _component_to_dict(self, comp: ComponentHealth) -> Dict[str, Any]:
        """Convert ComponentHealth to dictionary."""
        result = {
            "status": comp.status.value,
            "endpoint": comp.endpoint,
        }

        if comp.response_time_ms is not None:
            result["response_time_ms"] = comp.response_time_ms
        if comp.version is not None:
            result["version"] = comp.version
        if comp.uptime_seconds is not None:
            result["uptime_seconds"] = comp.uptime_seconds
        if comp.error is not None:
            result["error"] = comp.error
        if comp.details:
            result["details"] = comp.details

        return result

    def _connection_to_dict(self, conn: ConnectionHealth) -> Dict[str, Any]:
        """Convert ConnectionHealth to dictionary."""
        result = {
            "status": conn.status.value,
        }

        if conn.latency_ms is not None:
            result["latency_ms"] = conn.latency_ms
        if conn.error is not None:
            result["error"] = conn.error

        return result


# =============================================================================
# Factory Function (Clean Architecture Rule #1)
# =============================================================================
def create_ecosystem_health_manager(
    config_manager: ConfigManager,
    logger: LoggingConfigManager,
) -> EcosystemHealthManager:
    """
    Factory function to create an EcosystemHealthManager instance.

    Args:
        config_manager: Configuration manager instance
        logger: Logging manager instance

    Returns:
        Configured EcosystemHealthManager instance
    """
    return EcosystemHealthManager(
        config_manager=config_manager,
        logger=logger,
    )


__all__ = [
    "EcosystemHealthManager",
    "create_ecosystem_health_manager",
    "ComponentStatus",
    "ComponentHealth",
    "ConnectionHealth",
    "EcosystemHealth",
]
