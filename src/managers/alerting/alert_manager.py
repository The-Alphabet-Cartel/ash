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
Alert Manager - State Tracking and Transition Detection for Health Alerting
----------------------------------------------------------------------------
FILE VERSION: v5.0-4-1.1-1
LAST MODIFIED: 2026-01-18
PHASE: Phase 4 - Alerting Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from src.managers.config_manager import ConfigManager
from src.managers.ecosystem.ecosystem_health_manager import (
    ComponentStatus,
    EcosystemHealth,
)
from src.managers.logging_manager import LoggingConfigManager


# =============================================================================
# Alert Type Enum
# =============================================================================
class AlertType(str, Enum):
    """Types of alerts that can be generated."""

    CRITICAL = "critical"  # Component unreachable or unhealthy
    WARNING = "warning"  # Component degraded or connection issues
    RECOVERY = "recovery"  # Component recovered to healthy
    INFO = "info"  # Informational alerts


# =============================================================================
# Data Classes
# =============================================================================
@dataclass
class StatusTransition:
    """Represents a status change for a component or connection."""

    entity_type: str  # "component", "connection", or "ecosystem"
    entity_name: str  # Name of the component/connection
    from_status: ComponentStatus
    to_status: ComponentStatus
    timestamp: datetime
    alert_type: AlertType
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_critical(self) -> bool:
        """Check if this transition represents a critical alert."""
        return self.alert_type == AlertType.CRITICAL

    @property
    def is_recovery(self) -> bool:
        """Check if this transition represents a recovery."""
        return self.alert_type == AlertType.RECOVERY


@dataclass
class AlertState:
    """
    Tracks the current state of all monitored entities.

    Used to detect transitions between health checks.
    """

    # Status tracking per entity
    component_statuses: Dict[str, ComponentStatus] = field(default_factory=dict)
    connection_statuses: Dict[str, ComponentStatus] = field(default_factory=dict)
    ecosystem_status: ComponentStatus = ComponentStatus.HEALTHY

    # Cooldown tracking (entity_name -> last alert timestamp)
    last_alert_times: Dict[str, datetime] = field(default_factory=dict)

    # Downtime tracking (entity_name -> when it went down)
    downtime_start: Dict[str, datetime] = field(default_factory=dict)

    # Last health check timestamp
    last_check_time: Optional[datetime] = None

    # Flag to indicate if initial state has been established
    initialized: bool = False


# =============================================================================
# Alert Manager
# =============================================================================
class AlertManager:
    """
    Manages alert state tracking and transition detection.

    Features:
        - Tracks previous health state for all components and connections
        - Detects status transitions between health checks
        - Implements cooldown to prevent alert spam
        - Calculates downtime duration for recovery alerts
        - Supports configurable alert thresholds
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        logger: LoggingConfigManager,
    ):
        """
        Initialize the Alert Manager.

        Args:
            config_manager: Configuration manager instance
            logger: Logging manager instance
        """
        self._config = config_manager
        self._logger = logger
        self._log = logger.get_logger("alerting")

        # Initialize state
        self._state = AlertState()

        # Load configuration
        self._cooldown_seconds = self._config.alerting_cooldown_seconds
        self._alert_on_degraded = self._config.alerting_on_degraded
        self._alert_on_recovery = self._config.alerting_on_recovery
        self._alert_on_connection = self._config.alerting_on_connection_issues

        self._log.info("✅ AlertManager initialized")
        self._log.debug(
            f"   Cooldown: {self._cooldown_seconds}s, "
            f"Degraded alerts: {self._alert_on_degraded}, "
            f"Recovery alerts: {self._alert_on_recovery}"
        )

    def set_initial_state(self, health: EcosystemHealth) -> None:
        """
        Establish the initial state without triggering alerts.

        Called on startup to populate baseline state.

        Args:
            health: Current ecosystem health snapshot
        """
        self._log.info("📋 Establishing initial alert state (no alerts will fire)...")

        # Store component statuses
        for comp_key, comp_data in health.components.items():
            status_str = comp_data.get("status", "healthy")
            self._state.component_statuses[comp_key] = ComponentStatus(status_str)

        # Store connection statuses
        for conn_name, conn_data in health.connections.items():
            status_str = conn_data.get("status", "healthy")
            self._state.connection_statuses[conn_name] = ComponentStatus(status_str)

        # Store ecosystem status
        self._state.ecosystem_status = health.status

        # Mark as initialized
        self._state.last_check_time = datetime.now(timezone.utc)
        self._state.initialized = True

        self._log.info(
            f"✅ Initial state established: "
            f"{len(self._state.component_statuses)} components, "
            f"{len(self._state.connection_statuses)} connections, "
            f"ecosystem={health.status.value}"
        )

    def detect_transitions(self, current_health: EcosystemHealth) -> List[StatusTransition]:
        """
        Compare current health to previous state and detect transitions.

        Args:
            current_health: Current ecosystem health snapshot

        Returns:
            List of StatusTransition objects for all detected changes
        """
        if not self._state.initialized:
            self._log.warning("⚠️ Alert state not initialized, skipping transition detection")
            return []

        transitions: List[StatusTransition] = []
        now = datetime.now(timezone.utc)

        # Check component transitions
        for comp_key, comp_data in current_health.components.items():
            current_status = ComponentStatus(comp_data.get("status", "healthy"))
            previous_status = self._state.component_statuses.get(
                comp_key, ComponentStatus.HEALTHY
            )

            if current_status != previous_status:
                transition = self._create_transition(
                    entity_type="component",
                    entity_name=comp_key,
                    from_status=previous_status,
                    to_status=current_status,
                    timestamp=now,
                    error=comp_data.get("error"),
                    details=comp_data,
                )
                if transition:
                    transitions.append(transition)

                # Update state
                self._state.component_statuses[comp_key] = current_status

                # Track downtime
                self._update_downtime_tracking(comp_key, previous_status, current_status, now)

        # Check connection transitions (if configured)
        if self._alert_on_connection:
            for conn_name, conn_data in current_health.connections.items():
                current_status = ComponentStatus(conn_data.get("status", "healthy"))
                previous_status = self._state.connection_statuses.get(
                    conn_name, ComponentStatus.HEALTHY
                )

                if current_status != previous_status:
                    transition = self._create_transition(
                        entity_type="connection",
                        entity_name=conn_name,
                        from_status=previous_status,
                        to_status=current_status,
                        timestamp=now,
                        error=conn_data.get("error"),
                        details=conn_data,
                    )
                    if transition:
                        transitions.append(transition)

                    # Update state
                    self._state.connection_statuses[conn_name] = current_status

        # Check ecosystem-level transition
        if current_health.status != self._state.ecosystem_status:
            transition = self._create_transition(
                entity_type="ecosystem",
                entity_name="Ash Ecosystem",
                from_status=self._state.ecosystem_status,
                to_status=current_health.status,
                timestamp=now,
                details={"summary": current_health.summary},
            )
            if transition:
                transitions.append(transition)

            # Update state
            self._state.ecosystem_status = current_health.status

        # Update last check time
        self._state.last_check_time = now

        if transitions:
            self._log.info(f"🔔 Detected {len(transitions)} status transition(s)")
        else:
            self._log.debug("✅ No status transitions detected")

        return transitions

    def _create_transition(
        self,
        entity_type: str,
        entity_name: str,
        from_status: ComponentStatus,
        to_status: ComponentStatus,
        timestamp: datetime,
        error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Optional[StatusTransition]:
        """
        Create a StatusTransition with appropriate alert type.

        Args:
            entity_type: Type of entity (component, connection, ecosystem)
            entity_name: Name of the entity
            from_status: Previous status
            to_status: New status
            timestamp: When the transition occurred
            error: Error message if applicable
            details: Additional details

        Returns:
            StatusTransition object, or None if transition shouldn't generate alert
        """
        alert_type = self._determine_alert_type(from_status, to_status)

        # Check if we should generate this alert based on configuration
        if alert_type == AlertType.WARNING and not self._alert_on_degraded:
            self._log.debug(
                f"Skipping degraded alert for {entity_name} (alerts disabled)"
            )
            return None

        if alert_type == AlertType.RECOVERY and not self._alert_on_recovery:
            self._log.debug(
                f"Skipping recovery alert for {entity_name} (alerts disabled)"
            )
            return None

        # Add downtime duration for recovery alerts
        if details is None:
            details = {}

        if alert_type == AlertType.RECOVERY and entity_name in self._state.downtime_start:
            downtime_start = self._state.downtime_start[entity_name]
            downtime_seconds = (timestamp - downtime_start).total_seconds()
            details["downtime_seconds"] = int(downtime_seconds)
            details["downtime_formatted"] = self._format_duration(downtime_seconds)

        return StatusTransition(
            entity_type=entity_type,
            entity_name=entity_name,
            from_status=from_status,
            to_status=to_status,
            timestamp=timestamp,
            alert_type=alert_type,
            error=error,
            details=details,
        )

    def _determine_alert_type(
        self, from_status: ComponentStatus, to_status: ComponentStatus
    ) -> AlertType:
        """
        Determine the alert type based on status transition.

        Args:
            from_status: Previous status
            to_status: New status

        Returns:
            Appropriate AlertType for this transition
        """
        # Recovery: anything -> healthy
        if to_status == ComponentStatus.HEALTHY:
            return AlertType.RECOVERY

        # Critical: -> unreachable or unhealthy
        if to_status in (ComponentStatus.UNREACHABLE, ComponentStatus.UNHEALTHY):
            return AlertType.CRITICAL

        # Warning: -> degraded
        if to_status == ComponentStatus.DEGRADED:
            return AlertType.WARNING

        # Default to info for unusual transitions
        return AlertType.INFO

    def _update_downtime_tracking(
        self,
        entity_name: str,
        from_status: ComponentStatus,
        to_status: ComponentStatus,
        timestamp: datetime,
    ) -> None:
        """
        Update downtime tracking for an entity.

        Args:
            entity_name: Name of the entity
            from_status: Previous status
            to_status: New status
            timestamp: When the transition occurred
        """
        healthy_statuses = (ComponentStatus.HEALTHY, ComponentStatus.DISABLED)
        unhealthy_statuses = (
            ComponentStatus.DEGRADED,
            ComponentStatus.UNHEALTHY,
            ComponentStatus.UNREACHABLE,
        )

        # Started being unhealthy
        if from_status in healthy_statuses and to_status in unhealthy_statuses:
            self._state.downtime_start[entity_name] = timestamp
            self._log.debug(f"📉 Started tracking downtime for {entity_name}")

        # Recovered
        elif from_status in unhealthy_statuses and to_status in healthy_statuses:
            if entity_name in self._state.downtime_start:
                del self._state.downtime_start[entity_name]
                self._log.debug(f"📈 Cleared downtime tracking for {entity_name}")

    def should_alert(self, transition: StatusTransition) -> bool:
        """
        Check if an alert should be sent based on cooldown.

        Recovery alerts ALWAYS bypass cooldown - when something comes back up,
        we want to know immediately regardless of when the last alert was sent.

        Args:
            transition: The transition to check

        Returns:
            True if alert should be sent, False if in cooldown
        """
        # Recovery alerts ALWAYS bypass cooldown
        if transition.is_recovery:
            self._log.debug(
                f"✅ Recovery alert for {transition.entity_name} bypasses cooldown"
            )
            return True

        entity_key = f"{transition.entity_type}:{transition.entity_name}"
        last_alert = self._state.last_alert_times.get(entity_key)

        if last_alert is None:
            return True

        elapsed = (transition.timestamp - last_alert).total_seconds()

        if elapsed < self._cooldown_seconds:
            self._log.debug(
                f"⏳ Alert for {entity_key} in cooldown "
                f"({elapsed:.0f}s < {self._cooldown_seconds}s)"
            )
            return False

        return True

    def record_alert_sent(self, transition: StatusTransition) -> None:
        """
        Record that an alert was sent for cooldown tracking.

        Args:
            transition: The transition that was alerted on
        """
        entity_key = f"{transition.entity_type}:{transition.entity_name}"
        self._state.last_alert_times[entity_key] = transition.timestamp
        self._log.debug(f"📝 Recorded alert time for {entity_key}")

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """
        Format a duration in seconds to human-readable string.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted string (e.g., "5 mins", "2 hours 15 mins")
        """
        if seconds < 60:
            return f"{int(seconds)} secs"
        elif seconds < 3600:
            mins = int(seconds // 60)
            return f"{mins} min{'s' if mins != 1 else ''}"
        else:
            hours = int(seconds // 3600)
            mins = int((seconds % 3600) // 60)
            result = f"{hours} hour{'s' if hours != 1 else ''}"
            if mins > 0:
                result += f" {mins} min{'s' if mins != 1 else ''}"
            return result

    @property
    def is_initialized(self) -> bool:
        """Check if the alert state has been initialized."""
        return self._state.initialized

    @property
    def current_state(self) -> AlertState:
        """Get the current alert state (read-only access)."""
        return self._state


# =============================================================================
# Factory Function (Clean Architecture Rule #1)
# =============================================================================
def create_alert_manager(
    config_manager: ConfigManager,
    logger: LoggingConfigManager,
) -> AlertManager:
    """
    Factory function to create an AlertManager instance.

    Args:
        config_manager: Configuration manager instance
        logger: Logging manager instance

    Returns:
        Configured AlertManager instance
    """
    return AlertManager(
        config_manager=config_manager,
        logger=logger,
    )


__all__ = [
    "AlertManager",
    "AlertState",
    "AlertType",
    "StatusTransition",
    "create_alert_manager",
]
