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
Metrics Manager - Historical Health Data Storage and Retrieval
----------------------------------------------------------------------------
FILE VERSION: v5.0-5-2.1-1
LAST MODIFIED: 2026-01-18
PHASE: Phase 5 - Metrics & History
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash

PURPOSE:
    Manages historical health metrics storage and retrieval. Records ALL
    status transitions independently of AlertManager - this ensures complete
    audit trails regardless of alerting configuration.
============================================================================
"""

import json
from dataclasses import dataclass
from datetime import datetime, date, timezone, timedelta
from typing import Any, Dict, List, Optional

from src.managers.config_manager import ConfigManager
from src.managers.logging_manager import LoggingConfigManager
from src.managers.ecosystem.ecosystem_health_manager import (
    EcosystemHealth,
    ComponentStatus,
)
from src.managers.metrics.database import (
    HealthSnapshot,
    Incident,
    DailyAggregate,
    UptimeMetrics,
    MetricsDatabaseInterface,
    SQLiteMetricsDatabase,
)


# =============================================================================
# Cached State for Transition Detection
# =============================================================================
@dataclass
class EntityState:
    """Cached state for an entity (component or connection)."""

    status: str
    last_transition: datetime
    error_message: Optional[str] = None


# =============================================================================
# Metrics Manager
# =============================================================================
class MetricsManager:
    """
    Manages historical health metrics storage and retrieval.

    Independent of AlertManager - records ALL status transitions regardless
    of alerting configuration. This ensures:
        - Complete audit trail of all state changes
        - Historical data unaffected by alerting config changes
        - Accurate uptime calculations over any time period

    Features:
        - Snapshot storage (point-in-time health data)
        - Incident tracking (status transitions)
        - Automatic incident resolution detection
        - Uptime calculation from aggregates + raw snapshots
        - Daily aggregation for fast queries
        - Configurable retention cleanup
    """

    def __init__(
        self,
        database: MetricsDatabaseInterface,
        config_manager: ConfigManager,
        logger: Optional[LoggingConfigManager] = None,
    ):
        """
        Initialize the Metrics Manager.

        Args:
            database: Database interface for metrics storage
            config_manager: Configuration manager instance
            logger: Optional logging manager instance
        """
        self._db = database
        self._config = config_manager
        self._logger = logger
        self._log = logger.get_logger("metrics") if logger else None

        # Cache of last known states for transition detection
        self._entity_states: Dict[str, EntityState] = {}

        # Track last snapshot timestamp for duration calculations
        self._last_snapshot_time: Optional[datetime] = None

        self._log_info("✅ MetricsManager initialized")

    def _log_info(self, msg: str) -> None:
        if self._log:
            self._log.info(msg)

    def _log_debug(self, msg: str) -> None:
        if self._log:
            self._log.debug(msg)

    def _log_warning(self, msg: str) -> None:
        if self._log:
            self._log.warning(msg)

    def _log_error(self, msg: str) -> None:
        if self._log:
            self._log.error(msg)

    async def initialize(self) -> None:
        """
        Initialize the metrics database.

        Creates schema if needed and loads last known states for
        incident detection continuity.
        """
        # Initialize database schema
        await self._db.initialize()

        # Load last known states from most recent snapshot
        await self._load_last_known_states()

        self._log_info("✅ MetricsManager database initialized")

    async def _load_last_known_states(self) -> None:
        """
        Load last known entity states from the most recent snapshot.

        This ensures continuity of incident detection across restarts.
        """
        snapshot = await self._db.get_latest_snapshot()

        if not snapshot:
            self._log_debug("📋 No previous snapshots found - starting fresh")
            return

        self._last_snapshot_time = snapshot.timestamp
        self._log_debug(f"📋 Loading states from snapshot at {snapshot.timestamp}")

        # Load component states
        components = snapshot.components
        for name, data in components.items():
            if isinstance(data, dict):
                status = data.get("status", "unknown")
                error = data.get("error")
                self._entity_states[f"component:{name}"] = EntityState(
                    status=status,
                    last_transition=snapshot.timestamp,
                    error_message=error,
                )

        # Load connection states
        connections = snapshot.connections
        for name, data in connections.items():
            if isinstance(data, dict):
                status = data.get("status", "unknown")
                error = data.get("error")
                self._entity_states[f"connection:{name}"] = EntityState(
                    status=status,
                    last_transition=snapshot.timestamp,
                    error_message=error,
                )

        # Load ecosystem state
        self._entity_states["ecosystem:ash"] = EntityState(
            status=snapshot.ecosystem_status,
            last_transition=snapshot.timestamp,
        )

        self._log_debug(f"📋 Loaded {len(self._entity_states)} entity states")

    async def store_snapshot(
        self,
        health: EcosystemHealth,
        check_duration_ms: Optional[int] = None,
    ) -> int:
        """
        Store a health snapshot.

        Args:
            health: EcosystemHealth from the health check
            check_duration_ms: Duration of the health check in milliseconds

        Returns:
            ID of the stored snapshot
        """
        # Build the snapshot object
        snapshot = HealthSnapshot(
            timestamp=datetime.now(timezone.utc),
            ecosystem_status=health.status.value,
            components_json=json.dumps(health.components),
            connections_json=json.dumps(health.connections),
            check_duration_ms=check_duration_ms or health.meta.get("check_duration_ms"),
        )

        # Store in database
        snapshot_id = await self._db.store_snapshot(snapshot)

        # Update last snapshot time
        self._last_snapshot_time = snapshot.timestamp

        self._log_debug(f"📊 Stored snapshot #{snapshot_id}: {health.status.value}")

        return snapshot_id

    async def detect_and_record_incidents(
        self,
        current_health: EcosystemHealth,
    ) -> List[Incident]:
        """
        Compare current health to previous state and record any incidents.

        This is INDEPENDENT of AlertManager - always records transitions
        regardless of alerting configuration. This ensures:
            - Complete history even if alerting is disabled
            - Accurate uptime calculations
            - Full audit trail

        Args:
            current_health: Current EcosystemHealth from health check

        Returns:
            List of new Incident objects that were recorded
        """
        now = datetime.now(timezone.utc)
        new_incidents: List[Incident] = []

        # Check ecosystem status
        ecosystem_key = "ecosystem:ash"
        current_ecosystem_status = current_health.status.value
        prev_ecosystem = self._entity_states.get(ecosystem_key)

        if prev_ecosystem and prev_ecosystem.status != current_ecosystem_status:
            incident = await self._record_transition(
                entity_type="ecosystem",
                entity_name="ash",
                from_status=prev_ecosystem.status,
                to_status=current_ecosystem_status,
                timestamp=now,
                error_message=None,
            )
            if incident:
                new_incidents.append(incident)

        # Update ecosystem state
        self._entity_states[ecosystem_key] = EntityState(
            status=current_ecosystem_status,
            last_transition=now if prev_ecosystem and prev_ecosystem.status != current_ecosystem_status else (prev_ecosystem.last_transition if prev_ecosystem else now),
        )

        # Check each component
        for comp_name, comp_data in current_health.components.items():
            if not isinstance(comp_data, dict):
                continue

            component_key = f"component:{comp_name}"
            current_status = comp_data.get("status", "unknown")
            error_message = comp_data.get("error")

            prev_state = self._entity_states.get(component_key)

            if prev_state and prev_state.status != current_status:
                incident = await self._record_transition(
                    entity_type="component",
                    entity_name=comp_name,
                    from_status=prev_state.status,
                    to_status=current_status,
                    timestamp=now,
                    error_message=error_message,
                )
                if incident:
                    new_incidents.append(incident)

            # Update component state
            self._entity_states[component_key] = EntityState(
                status=current_status,
                last_transition=now if prev_state and prev_state.status != current_status else (prev_state.last_transition if prev_state else now),
                error_message=error_message,
            )

        # Check each connection
        for conn_name, conn_data in current_health.connections.items():
            if not isinstance(conn_data, dict):
                continue

            connection_key = f"connection:{conn_name}"
            current_status = conn_data.get("status", "unknown")
            error_message = conn_data.get("error")

            prev_state = self._entity_states.get(connection_key)

            if prev_state and prev_state.status != current_status:
                incident = await self._record_transition(
                    entity_type="connection",
                    entity_name=conn_name,
                    from_status=prev_state.status,
                    to_status=current_status,
                    timestamp=now,
                    error_message=error_message,
                )
                if incident:
                    new_incidents.append(incident)

            # Update connection state
            self._entity_states[connection_key] = EntityState(
                status=current_status,
                last_transition=now if prev_state and prev_state.status != current_status else (prev_state.last_transition if prev_state else now),
                error_message=error_message,
            )

        if new_incidents:
            self._log_info(f"📝 Recorded {len(new_incidents)} new incident(s)")

        return new_incidents

    async def _record_transition(
        self,
        entity_type: str,
        entity_name: str,
        from_status: str,
        to_status: str,
        timestamp: datetime,
        error_message: Optional[str] = None,
    ) -> Optional[Incident]:
        """
        Record a status transition as an incident.

        Also handles resolution of previous incidents when transitioning
        back to healthy status.

        Args:
            entity_type: Type of entity (component, connection, ecosystem)
            entity_name: Name of the entity
            from_status: Previous status
            to_status: New status
            timestamp: When the transition occurred
            error_message: Optional error message for the new state

        Returns:
            The recorded Incident, or None if recording failed
            Returns None for transitions TO healthy (these are resolutions, not incidents)
        """
        # If transitioning TO healthy, resolve any open incidents and return
        # Recovery is the RESOLUTION of an incident, not a new incident itself
        if to_status == "healthy":
            # Calculate duration from the last transition
            entity_key = f"{entity_type}:{entity_name}"
            prev_state = self._entity_states.get(entity_key)

            if prev_state:
                duration = int((timestamp - prev_state.last_transition).total_seconds())
                await self._db.resolve_incident(
                    entity_type=entity_type,
                    entity_name=entity_name,
                    resolved_at=timestamp,
                    duration_seconds=duration,
                )
                self._log_info(
                    f"✅ Resolved: {entity_name} recovered after {duration}s"
                )

            # Don't create an incident for recovery - it's already tracked
            # via resolved_at on the original incident
            return None

        # Record the new incident (only for non-healthy transitions)
        incident = Incident(
            timestamp=timestamp,
            entity_type=entity_type,
            entity_name=entity_name,
            from_status=from_status,
            to_status=to_status,
            error_message=error_message,
        )

        try:
            incident_id = await self._db.record_incident(incident)
            incident.id = incident_id
            self._log_info(
                f"📝 Incident #{incident_id}: {entity_name} "
                f"{from_status} → {to_status}"
            )
            return incident
        except Exception as e:
            self._log_error(f"❌ Failed to record incident: {e}")
            return None

    async def get_uptime(
        self,
        component: Optional[str] = None,
        days: int = 30,
    ) -> Dict[str, UptimeMetrics]:
        """
        Calculate uptime metrics for a period.

        Uses daily aggregates for efficiency, with raw snapshots for
        the current (incomplete) day.

        Args:
            component: Filter to specific component (None = all)
            days: Number of days to calculate (1-90)

        Returns:
            Dictionary of component name to UptimeMetrics
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        # Get daily aggregates
        aggregates = await self._db.get_daily_aggregates(
            component=component,
            start_date=start_date,
            end_date=end_date,
        )

        # Group aggregates by component
        component_data: Dict[str, List[DailyAggregate]] = {}
        for agg in aggregates:
            if agg.component not in component_data:
                component_data[agg.component] = []
            component_data[agg.component].append(agg)

        # Calculate metrics for each component
        results: Dict[str, UptimeMetrics] = {}
        period_start = datetime.combine(start_date, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        period_end = datetime.combine(end_date, datetime.max.time()).replace(
            tzinfo=timezone.utc
        )

        for comp_name, agg_list in component_data.items():
            # Sum up the aggregates
            total_healthy = sum(a.healthy_seconds for a in agg_list)
            total_degraded = sum(a.degraded_seconds for a in agg_list)
            total_unhealthy = sum(a.unhealthy_seconds for a in agg_list)
            total_unreachable = sum(a.unreachable_seconds for a in agg_list)
            total_incidents = sum(a.incident_count for a in agg_list)

            total_seconds = (
                total_healthy + total_degraded + total_unhealthy + total_unreachable
            )

            # Calculate MTTR from resolved incidents
            mttr = await self._calculate_mttr(comp_name, period_start, period_end)

            results[comp_name] = UptimeMetrics(
                component=comp_name,
                period_start=period_start,
                period_end=period_end,
                total_seconds=total_seconds,
                healthy_seconds=total_healthy,
                degraded_seconds=total_degraded,
                unhealthy_seconds=total_unhealthy,
                unreachable_seconds=total_unreachable,
                incident_count=total_incidents,
                mttr_seconds=mttr,
            )

        # If no aggregates exist but we have snapshots, calculate from snapshots
        if not results and component is None:
            results = await self._calculate_uptime_from_snapshots(
                period_start, period_end
            )

        return results

    async def _calculate_mttr(
        self,
        component: str,
        start: datetime,
        end: datetime,
    ) -> Optional[int]:
        """
        Calculate Mean Time To Recovery for a component.

        Args:
            component: Component name
            start: Period start
            end: Period end

        Returns:
            MTTR in seconds, or None if no resolved incidents
        """
        incidents = await self._db.get_incidents(
            entity_name=component,
            start=start,
            end=end,
        )

        # Filter to resolved incidents with duration
        resolved = [
            i for i in incidents
            if i.duration_seconds is not None and i.duration_seconds > 0
        ]

        if not resolved:
            return None

        total_duration = sum(i.duration_seconds for i in resolved if i.duration_seconds)
        return total_duration // len(resolved)

    async def _calculate_uptime_from_snapshots(
        self,
        start: datetime,
        end: datetime,
    ) -> Dict[str, UptimeMetrics]:
        """
        Calculate uptime directly from raw snapshots.

        Used as fallback when no aggregates exist.

        Args:
            start: Period start
            end: Period end

        Returns:
            Dictionary of component name to UptimeMetrics
        """
        snapshots = await self._db.get_snapshots(start, end, limit=10000)

        if not snapshots:
            return {}

        # Track seconds per status per component
        component_stats: Dict[str, Dict[str, int]] = {}

        # Assume each snapshot represents ~60 seconds (or use actual interval)
        interval_seconds = 60

        for snapshot in snapshots:
            components = snapshot.components
            for comp_name, comp_data in components.items():
                if comp_name not in component_stats:
                    component_stats[comp_name] = {
                        "healthy": 0,
                        "degraded": 0,
                        "unhealthy": 0,
                        "unreachable": 0,
                        "disabled": 0,
                    }

                status = comp_data.get("status", "unknown") if isinstance(comp_data, dict) else "unknown"
                if status in component_stats[comp_name]:
                    component_stats[comp_name][status] += interval_seconds

        # Build UptimeMetrics objects
        results: Dict[str, UptimeMetrics] = {}
        for comp_name, stats in component_stats.items():
            total = sum(stats.values())
            results[comp_name] = UptimeMetrics(
                component=comp_name,
                period_start=start,
                period_end=end,
                total_seconds=total,
                healthy_seconds=stats["healthy"],
                degraded_seconds=stats["degraded"],
                unhealthy_seconds=stats["unhealthy"],
                unreachable_seconds=stats["unreachable"],
                incident_count=0,  # Would need to count from incident table
            )

        return results

    async def get_incidents(
        self,
        component: Optional[str] = None,
        days: int = 30,
        limit: int = 100,
    ) -> List[Incident]:
        """
        Retrieve incident history.

        Args:
            component: Filter to specific component (None = all)
            days: Number of days of history (1-90)
            limit: Maximum number of incidents to return

        Returns:
            List of Incidents, ordered by timestamp descending
        """
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)

        return await self._db.get_incidents(
            entity_name=component,
            start=start,
            end=end,
            limit=limit,
        )

    async def aggregate_daily(self, target_date: date) -> None:
        """
        Compute and store daily aggregates for a specific date.

        Processes all snapshots for the target date and creates
        aggregated statistics for each component.

        Args:
            target_date: The date to aggregate (should be a past date)
        """
        self._log_info(f"📊 Aggregating data for {target_date}")

        # Get all snapshots for the target date
        start = datetime.combine(target_date, datetime.min.time()).replace(
            tzinfo=timezone.utc
        )
        end = datetime.combine(target_date, datetime.max.time()).replace(
            tzinfo=timezone.utc
        )

        snapshots = await self._db.get_snapshots(start, end, limit=2000)

        if not snapshots:
            self._log_debug(f"📋 No snapshots found for {target_date}")
            return

        # Track seconds per status per component
        component_stats: Dict[str, Dict[str, int]] = {}

        # Assume each snapshot represents ~60 seconds
        interval_seconds = 60

        for snapshot in snapshots:
            components = snapshot.components
            for comp_name, comp_data in components.items():
                if comp_name not in component_stats:
                    component_stats[comp_name] = {
                        "healthy": 0,
                        "degraded": 0,
                        "unhealthy": 0,
                        "unreachable": 0,
                    }

                status = comp_data.get("status", "unknown") if isinstance(comp_data, dict) else "unknown"
                if status in component_stats[comp_name]:
                    component_stats[comp_name][status] += interval_seconds

        # Count incidents per component for the day
        incidents = await self._db.get_incidents(start=start, end=end)
        incident_counts: Dict[str, int] = {}
        for inc in incidents:
            if inc.entity_type == "component":
                incident_counts[inc.entity_name] = incident_counts.get(inc.entity_name, 0) + 1

        # Store aggregates
        for comp_name, stats in component_stats.items():
            aggregate = DailyAggregate(
                date=target_date.isoformat(),
                component=comp_name,
                healthy_seconds=stats["healthy"],
                degraded_seconds=stats["degraded"],
                unhealthy_seconds=stats["unhealthy"],
                unreachable_seconds=stats["unreachable"],
                incident_count=incident_counts.get(comp_name, 0),
            )
            await self._db.store_daily_aggregate(aggregate)

        self._log_info(
            f"✅ Aggregated {len(component_stats)} components for {target_date}"
        )

    async def cleanup_old_data(self) -> Dict[str, int]:
        """
        Delete data older than configured retention periods.

        Returns:
            Dictionary with counts of deleted rows per table
        """
        # Get retention configuration
        snapshots_days = self._config.metrics_retention_snapshots_days
        incidents_days = self._config.metrics_retention_incidents_days
        aggregates_days = self._config.metrics_retention_aggregates_days

        self._log_info(
            f"🗑️ Running cleanup (snapshots: {snapshots_days}d, "
            f"incidents: {incidents_days}d, aggregates: {aggregates_days}d)"
        )

        deleted = await self._db.cleanup_old_data(
            snapshots_days=snapshots_days,
            incidents_days=incidents_days,
            aggregates_days=aggregates_days,
        )

        total = sum(deleted.values())
        if total > 0:
            self._log_info(f"✅ Cleanup complete: {total} records deleted")
        else:
            self._log_debug("✅ Cleanup complete: no old data to delete")

        return deleted

    async def daily_maintenance(self) -> None:
        """
        Perform daily maintenance tasks.

        Should be called once per day (typically at configured maintenance hour):
            1. Aggregate yesterday's snapshots
            2. Clean up old data based on retention policy
        """
        yesterday = date.today() - timedelta(days=1)

        self._log_info(f"🔧 Starting daily maintenance for {yesterday}")

        # Aggregate yesterday's data
        await self.aggregate_daily(yesterday)

        # Clean up old data
        await self.cleanup_old_data()

        self._log_info("✅ Daily maintenance complete")

    async def close(self) -> None:
        """Close the metrics manager and database connection."""
        await self._db.close()
        self._log_info("🔌 MetricsManager closed")


# =============================================================================
# Factory Function (Clean Architecture Rule #1)
# =============================================================================
def create_metrics_manager(
    config_manager: ConfigManager,
    logger: Optional[LoggingConfigManager] = None,
) -> MetricsManager:
    """
    Factory function to create a MetricsManager instance.

    Creates the SQLite database and MetricsManager with proper
    dependency injection.

    Args:
        config_manager: Configuration manager instance
        logger: Optional logging manager instance

    Returns:
        Configured MetricsManager instance

    Note:
        Call initialize() on the returned instance to set up the database schema.
    """
    # Get database path from config
    db_path = config_manager.metrics_db_path

    # Create database instance
    database = SQLiteMetricsDatabase(
        db_path=db_path,
        logger=logger,
    )

    # Create and return MetricsManager
    return MetricsManager(
        database=database,
        config_manager=config_manager,
        logger=logger,
    )


__all__ = [
    "MetricsManager",
    "create_metrics_manager",
    "EntityState",
]
