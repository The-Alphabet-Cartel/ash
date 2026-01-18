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
Metrics Database - SQLite Implementation with PostgreSQL Migration Support
----------------------------------------------------------------------------
FILE VERSION: v5.0-5-1.0-1
LAST MODIFIED: 2026-01-17
PHASE: Phase 5 - Metrics & History
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash

MIGRATION GUIDELINES:
    - Uses standard SQL syntax (no SQLite-specific functions)
    - Uses INTEGER PRIMARY KEY (works in both SQLite and PostgreSQL)
    - Stores timestamps as ISO 8601 TEXT strings
    - Uses parameterized queries with ? placeholders
    - Avoids AUTOINCREMENT keyword
    - Uses 1/0 for booleans instead of TRUE/FALSE literals
    - All LIMIT queries include ORDER BY clause
    
    See docs/v5.0/phase5/planning.md for full migration guidelines.
============================================================================
"""

import json
import aiosqlite
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, date, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.managers.logging_manager import LoggingConfigManager


# =============================================================================
# Data Classes
# =============================================================================
@dataclass
class HealthSnapshot:
    """
    Point-in-time ecosystem health snapshot.
    
    Stored every health check cycle (default: 60 seconds).
    """
    timestamp: datetime
    ecosystem_status: str
    components_json: str  # JSON blob as TEXT
    connections_json: str  # JSON blob as TEXT
    check_duration_ms: Optional[int] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @property
    def components(self) -> Dict[str, Any]:
        """Parse components JSON into dict."""
        return json.loads(self.components_json) if self.components_json else {}

    @property
    def connections(self) -> Dict[str, Any]:
        """Parse connections JSON into dict."""
        return json.loads(self.connections_json) if self.connections_json else {}


@dataclass
class Incident:
    """
    Status transition event.
    
    Recorded independently of alerting configuration - captures ALL
    status transitions for complete audit trail.
    """
    timestamp: datetime
    entity_type: str  # "component", "connection", or "ecosystem"
    entity_name: str
    from_status: str
    to_status: str
    error_message: Optional[str] = None
    duration_seconds: Optional[int] = None
    resolved_at: Optional[datetime] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @property
    def is_resolved(self) -> bool:
        """Check if this incident has been resolved."""
        return self.resolved_at is not None

    @property
    def is_recovery(self) -> bool:
        """Check if this incident represents a recovery to healthy status."""
        return self.to_status == "healthy"


@dataclass
class DailyAggregate:
    """
    Pre-computed daily statistics for fast uptime queries.
    
    Computed daily from raw snapshots, then snapshots are purged
    according to retention policy.
    """
    date: str  # YYYY-MM-DD format
    component: str
    healthy_seconds: int = 0
    degraded_seconds: int = 0
    unhealthy_seconds: int = 0
    unreachable_seconds: int = 0
    incident_count: int = 0
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    @property
    def total_seconds(self) -> int:
        """Total seconds tracked for the day."""
        return (
            self.healthy_seconds
            + self.degraded_seconds
            + self.unhealthy_seconds
            + self.unreachable_seconds
        )

    @property
    def uptime_seconds(self) -> int:
        """Seconds considered 'up' (healthy + degraded)."""
        return self.healthy_seconds + self.degraded_seconds

    @property
    def uptime_percentage(self) -> float:
        """Uptime percentage for the day."""
        if self.total_seconds == 0:
            return 100.0
        return (self.uptime_seconds / self.total_seconds) * 100.0


@dataclass
class UptimeMetrics:
    """
    Computed uptime statistics for a period.
    
    Calculated at query time from daily aggregates and/or raw snapshots.
    """
    component: str
    period_start: datetime
    period_end: datetime
    total_seconds: int = 0
    healthy_seconds: int = 0
    degraded_seconds: int = 0
    unhealthy_seconds: int = 0
    unreachable_seconds: int = 0
    incident_count: int = 0
    mttr_seconds: Optional[int] = None  # Mean Time To Recovery

    @property
    def uptime_seconds(self) -> int:
        """Seconds considered 'up' (healthy + degraded)."""
        return self.healthy_seconds + self.degraded_seconds

    @property
    def uptime_percentage(self) -> float:
        """Uptime percentage for the period."""
        if self.total_seconds == 0:
            return 100.0
        return (self.uptime_seconds / self.total_seconds) * 100.0

    @property
    def healthy_percentage(self) -> float:
        """Percentage of time in healthy state."""
        if self.total_seconds == 0:
            return 100.0
        return (self.healthy_seconds / self.total_seconds) * 100.0

    @property
    def degraded_percentage(self) -> float:
        """Percentage of time in degraded state."""
        if self.total_seconds == 0:
            return 0.0
        return (self.degraded_seconds / self.total_seconds) * 100.0


# =============================================================================
# Database Schema
# =============================================================================
SCHEMA_SQL = """
-- Health snapshots (one per check cycle)
-- Migration note: INTEGER PRIMARY KEY auto-increments in SQLite
-- PostgreSQL equivalent: SERIAL PRIMARY KEY
CREATE TABLE IF NOT EXISTS health_snapshots (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    ecosystem_status TEXT NOT NULL,
    check_duration_ms INTEGER,
    components_json TEXT NOT NULL,
    connections_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON health_snapshots(timestamp);
CREATE INDEX IF NOT EXISTS idx_snapshots_status ON health_snapshots(ecosystem_status);

-- Incidents (status transitions - independent of alerting)
CREATE TABLE IF NOT EXISTS incidents (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    error_message TEXT,
    duration_seconds INTEGER,
    resolved_at TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_incidents_timestamp ON incidents(timestamp);
CREATE INDEX IF NOT EXISTS idx_incidents_entity ON incidents(entity_name);
CREATE INDEX IF NOT EXISTS idx_incidents_resolved ON incidents(resolved_at);
CREATE INDEX IF NOT EXISTS idx_incidents_entity_type ON incidents(entity_type);

-- Daily aggregates (for fast uptime queries)
CREATE TABLE IF NOT EXISTS daily_aggregates (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    component TEXT NOT NULL,
    healthy_seconds INTEGER DEFAULT 0,
    degraded_seconds INTEGER DEFAULT 0,
    unhealthy_seconds INTEGER DEFAULT 0,
    unreachable_seconds INTEGER DEFAULT 0,
    incident_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    UNIQUE(date, component)
);

CREATE INDEX IF NOT EXISTS idx_aggregates_date ON daily_aggregates(date);
CREATE INDEX IF NOT EXISTS idx_aggregates_component ON daily_aggregates(component);

-- Schema version tracking (for future migrations)
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT
);
"""

CURRENT_SCHEMA_VERSION = 1


# =============================================================================
# Abstract Interface
# =============================================================================
class MetricsDatabaseInterface(ABC):
    """
    Abstract interface for metrics storage.
    
    Enables future PostgreSQL migration by hiding implementation details.
    All implementations must follow the migration guidelines in the
    planning document.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize database schema."""
        ...

    @abstractmethod
    async def store_snapshot(self, snapshot: HealthSnapshot) -> int:
        """
        Store a health snapshot.
        
        Args:
            snapshot: HealthSnapshot to store
            
        Returns:
            ID of the inserted snapshot
        """
        ...

    @abstractmethod
    async def get_latest_snapshot(self) -> Optional[HealthSnapshot]:
        """
        Get the most recent health snapshot.
        
        Returns:
            Most recent HealthSnapshot or None if no snapshots exist
        """
        ...

    @abstractmethod
    async def get_snapshots(
        self,
        start: datetime,
        end: datetime,
        limit: int = 1000,
    ) -> List[HealthSnapshot]:
        """
        Get snapshots within a time range.
        
        Args:
            start: Start of time range (inclusive)
            end: End of time range (inclusive)
            limit: Maximum number of snapshots to return
            
        Returns:
            List of HealthSnapshots, ordered by timestamp descending
        """
        ...

    @abstractmethod
    async def record_incident(self, incident: Incident) -> int:
        """
        Record a new incident.
        
        Args:
            incident: Incident to record
            
        Returns:
            ID of the inserted incident
        """
        ...

    @abstractmethod
    async def resolve_incident(
        self,
        entity_type: str,
        entity_name: str,
        resolved_at: datetime,
        duration_seconds: int,
    ) -> int:
        """
        Mark the most recent unresolved incident for an entity as resolved.
        
        Args:
            entity_type: Type of entity (component, connection, ecosystem)
            entity_name: Name of the entity
            resolved_at: When the incident was resolved
            duration_seconds: Duration of the incident in seconds
            
        Returns:
            Number of incidents updated (0 or 1)
        """
        ...

    @abstractmethod
    async def get_incidents(
        self,
        entity_name: Optional[str] = None,
        entity_type: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Incident]:
        """
        Retrieve incident history.
        
        Args:
            entity_name: Filter by entity name (optional)
            entity_type: Filter by entity type (optional)
            start: Start of time range (optional)
            end: End of time range (optional)
            limit: Maximum number of incidents to return
            
        Returns:
            List of Incidents, ordered by timestamp descending
        """
        ...

    @abstractmethod
    async def get_open_incidents(self) -> List[Incident]:
        """
        Get all unresolved incidents.
        
        Returns:
            List of Incidents where resolved_at is NULL
        """
        ...

    @abstractmethod
    async def store_daily_aggregate(self, aggregate: DailyAggregate) -> int:
        """
        Store or update a daily aggregate.
        
        Uses upsert semantics - updates if exists, inserts if not.
        
        Args:
            aggregate: DailyAggregate to store
            
        Returns:
            ID of the inserted/updated aggregate
        """
        ...

    @abstractmethod
    async def get_daily_aggregates(
        self,
        component: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[DailyAggregate]:
        """
        Get daily aggregates for uptime calculation.
        
        Args:
            component: Filter by component (optional, None = all)
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            List of DailyAggregates, ordered by date descending
        """
        ...

    @abstractmethod
    async def cleanup_old_data(
        self,
        snapshots_days: int,
        incidents_days: int,
        aggregates_days: int,
    ) -> Dict[str, int]:
        """
        Delete data older than retention periods.
        
        Args:
            snapshots_days: Delete snapshots older than this many days
            incidents_days: Delete incidents older than this many days
            aggregates_days: Delete aggregates older than this many days
            
        Returns:
            Dict with counts of deleted rows per table
        """
        ...

    @abstractmethod
    async def get_snapshot_count(self, since: Optional[datetime] = None) -> int:
        """
        Get count of snapshots.
        
        Args:
            since: Only count snapshots after this time (optional)
            
        Returns:
            Number of snapshots
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Close database connection."""
        ...


# =============================================================================
# SQLite Implementation
# =============================================================================
class SQLiteMetricsDatabase(MetricsDatabaseInterface):
    """
    SQLite implementation of metrics storage.
    
    Follows migration guidelines for future PostgreSQL compatibility:
        - Uses standard SQL syntax
        - Uses INTEGER PRIMARY KEY (no AUTOINCREMENT)
        - Stores timestamps as ISO 8601 TEXT strings
        - Uses parameterized queries with ? placeholders
        - All LIMIT queries include ORDER BY clause
    """

    def __init__(
        self,
        db_path: str,
        logger: Optional[LoggingConfigManager] = None,
    ):
        """
        Initialize the SQLite metrics database.
        
        Args:
            db_path: Path to the SQLite database file
            logger: Optional logging manager instance
        """
        self._db_path = Path(db_path)
        self._logger = logger
        self._log = logger.get_logger("metrics_db") if logger else None
        self._connection: Optional[aiosqlite.Connection] = None

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

    @staticmethod
    def _now_iso() -> str:
        """Get current UTC time as ISO 8601 string."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _datetime_to_iso(dt: datetime) -> str:
        """Convert datetime to ISO 8601 string."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def _iso_to_datetime(iso_str: str) -> datetime:
        """Convert ISO 8601 string to datetime."""
        # Handle various ISO formats
        for fmt in (
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ):
            try:
                dt = datetime.strptime(iso_str, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        # Fallback - try to parse as-is
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

    async def _get_connection(self) -> aiosqlite.Connection:
        """Get or create database connection."""
        if self._connection is None:
            # Ensure parent directory exists
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self._connection = await aiosqlite.connect(str(self._db_path))
            # Enable foreign keys
            await self._connection.execute("PRAGMA foreign_keys = ON")
            # Use WAL mode for better concurrent read performance
            await self._connection.execute("PRAGMA journal_mode = WAL")
            
        return self._connection

    async def initialize(self) -> None:
        """Initialize database schema."""
        conn = await self._get_connection()
        
        # Check current schema version
        try:
            cursor = await conn.execute(
                "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
            )
            row = await cursor.fetchone()
            current_version = row[0] if row else 0
        except aiosqlite.OperationalError:
            # Table doesn't exist yet
            current_version = 0

        if current_version < CURRENT_SCHEMA_VERSION:
            self._log_info(f"🔧 Initializing metrics database schema (v{CURRENT_SCHEMA_VERSION})...")
            
            # Execute schema creation
            await conn.executescript(SCHEMA_SQL)
            
            # Record schema version
            await conn.execute(
                """
                INSERT OR REPLACE INTO schema_version (version, applied_at, description)
                VALUES (?, ?, ?)
                """,
                (
                    CURRENT_SCHEMA_VERSION,
                    self._now_iso(),
                    "Initial schema with snapshots, incidents, and daily_aggregates",
                ),
            )
            await conn.commit()
            
            self._log_info(f"✅ Metrics database initialized at {self._db_path}")
        else:
            self._log_debug(f"📋 Metrics database already at schema v{current_version}")

    async def store_snapshot(self, snapshot: HealthSnapshot) -> int:
        """Store a health snapshot."""
        conn = await self._get_connection()
        
        cursor = await conn.execute(
            """
            INSERT INTO health_snapshots 
                (timestamp, ecosystem_status, check_duration_ms, components_json, connections_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                self._datetime_to_iso(snapshot.timestamp),
                snapshot.ecosystem_status,
                snapshot.check_duration_ms,
                snapshot.components_json,
                snapshot.connections_json,
                self._now_iso(),
            ),
        )
        await conn.commit()
        
        snapshot_id = cursor.lastrowid
        self._log_debug(f"📊 Stored snapshot #{snapshot_id}: {snapshot.ecosystem_status}")
        return snapshot_id

    async def get_latest_snapshot(self) -> Optional[HealthSnapshot]:
        """Get the most recent health snapshot."""
        conn = await self._get_connection()
        
        cursor = await conn.execute(
            """
            SELECT id, timestamp, ecosystem_status, check_duration_ms, 
                   components_json, connections_json, created_at
            FROM health_snapshots
            ORDER BY timestamp DESC
            LIMIT 1
            """
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
            
        return HealthSnapshot(
            id=row[0],
            timestamp=self._iso_to_datetime(row[1]),
            ecosystem_status=row[2],
            check_duration_ms=row[3],
            components_json=row[4],
            connections_json=row[5],
            created_at=self._iso_to_datetime(row[6]) if row[6] else None,
        )

    async def get_snapshots(
        self,
        start: datetime,
        end: datetime,
        limit: int = 1000,
    ) -> List[HealthSnapshot]:
        """Get snapshots within a time range."""
        conn = await self._get_connection()
        
        cursor = await conn.execute(
            """
            SELECT id, timestamp, ecosystem_status, check_duration_ms,
                   components_json, connections_json, created_at
            FROM health_snapshots
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (
                self._datetime_to_iso(start),
                self._datetime_to_iso(end),
                limit,
            ),
        )
        rows = await cursor.fetchall()
        
        return [
            HealthSnapshot(
                id=row[0],
                timestamp=self._iso_to_datetime(row[1]),
                ecosystem_status=row[2],
                check_duration_ms=row[3],
                components_json=row[4],
                connections_json=row[5],
                created_at=self._iso_to_datetime(row[6]) if row[6] else None,
            )
            for row in rows
        ]

    async def record_incident(self, incident: Incident) -> int:
        """Record a new incident."""
        conn = await self._get_connection()
        
        cursor = await conn.execute(
            """
            INSERT INTO incidents
                (timestamp, entity_type, entity_name, from_status, to_status,
                 error_message, duration_seconds, resolved_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self._datetime_to_iso(incident.timestamp),
                incident.entity_type,
                incident.entity_name,
                incident.from_status,
                incident.to_status,
                incident.error_message,
                incident.duration_seconds,
                self._datetime_to_iso(incident.resolved_at) if incident.resolved_at else None,
                self._now_iso(),
            ),
        )
        await conn.commit()
        
        incident_id = cursor.lastrowid
        self._log_info(
            f"📝 Recorded incident #{incident_id}: {incident.entity_name} "
            f"{incident.from_status} → {incident.to_status}"
        )
        return incident_id

    async def resolve_incident(
        self,
        entity_type: str,
        entity_name: str,
        resolved_at: datetime,
        duration_seconds: int,
    ) -> int:
        """Mark the most recent unresolved incident for an entity as resolved."""
        conn = await self._get_connection()
        
        # Find the most recent unresolved incident for this entity
        cursor = await conn.execute(
            """
            UPDATE incidents
            SET resolved_at = ?, duration_seconds = ?
            WHERE id = (
                SELECT id FROM incidents
                WHERE entity_type = ? AND entity_name = ? AND resolved_at IS NULL
                ORDER BY timestamp DESC
                LIMIT 1
            )
            """,
            (
                self._datetime_to_iso(resolved_at),
                duration_seconds,
                entity_type,
                entity_name,
            ),
        )
        await conn.commit()
        
        updated = cursor.rowcount
        if updated > 0:
            self._log_info(
                f"✅ Resolved incident for {entity_name} "
                f"(duration: {duration_seconds}s)"
            )
        return updated

    async def get_incidents(
        self,
        entity_name: Optional[str] = None,
        entity_type: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Incident]:
        """Retrieve incident history."""
        conn = await self._get_connection()
        
        # Build query dynamically based on filters
        conditions = []
        params = []
        
        if entity_name is not None:
            conditions.append("entity_name = ?")
            params.append(entity_name)
            
        if entity_type is not None:
            conditions.append("entity_type = ?")
            params.append(entity_type)
            
        if start is not None:
            conditions.append("timestamp >= ?")
            params.append(self._datetime_to_iso(start))
            
        if end is not None:
            conditions.append("timestamp <= ?")
            params.append(self._datetime_to_iso(end))
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)
        
        cursor = await conn.execute(
            f"""
            SELECT id, timestamp, entity_type, entity_name, from_status, to_status,
                   error_message, duration_seconds, resolved_at, created_at
            FROM incidents
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            params,
        )
        rows = await cursor.fetchall()
        
        return [
            Incident(
                id=row[0],
                timestamp=self._iso_to_datetime(row[1]),
                entity_type=row[2],
                entity_name=row[3],
                from_status=row[4],
                to_status=row[5],
                error_message=row[6],
                duration_seconds=row[7],
                resolved_at=self._iso_to_datetime(row[8]) if row[8] else None,
                created_at=self._iso_to_datetime(row[9]) if row[9] else None,
            )
            for row in rows
        ]

    async def get_open_incidents(self) -> List[Incident]:
        """Get all unresolved incidents."""
        conn = await self._get_connection()
        
        cursor = await conn.execute(
            """
            SELECT id, timestamp, entity_type, entity_name, from_status, to_status,
                   error_message, duration_seconds, resolved_at, created_at
            FROM incidents
            WHERE resolved_at IS NULL
            ORDER BY timestamp DESC
            """
        )
        rows = await cursor.fetchall()
        
        return [
            Incident(
                id=row[0],
                timestamp=self._iso_to_datetime(row[1]),
                entity_type=row[2],
                entity_name=row[3],
                from_status=row[4],
                to_status=row[5],
                error_message=row[6],
                duration_seconds=row[7],
                resolved_at=None,
                created_at=self._iso_to_datetime(row[9]) if row[9] else None,
            )
            for row in rows
        ]

    async def store_daily_aggregate(self, aggregate: DailyAggregate) -> int:
        """Store or update a daily aggregate (upsert)."""
        conn = await self._get_connection()
        
        # SQLite upsert using INSERT OR REPLACE
        # Note: This works because we have UNIQUE(date, component)
        cursor = await conn.execute(
            """
            INSERT INTO daily_aggregates
                (date, component, healthy_seconds, degraded_seconds,
                 unhealthy_seconds, unreachable_seconds, incident_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date, component) DO UPDATE SET
                healthy_seconds = excluded.healthy_seconds,
                degraded_seconds = excluded.degraded_seconds,
                unhealthy_seconds = excluded.unhealthy_seconds,
                unreachable_seconds = excluded.unreachable_seconds,
                incident_count = excluded.incident_count
            """,
            (
                aggregate.date,
                aggregate.component,
                aggregate.healthy_seconds,
                aggregate.degraded_seconds,
                aggregate.unhealthy_seconds,
                aggregate.unreachable_seconds,
                aggregate.incident_count,
                self._now_iso(),
            ),
        )
        await conn.commit()
        
        self._log_debug(
            f"📈 Stored aggregate for {aggregate.component} on {aggregate.date}: "
            f"{aggregate.uptime_percentage:.1f}% uptime"
        )
        return cursor.lastrowid

    async def get_daily_aggregates(
        self,
        component: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[DailyAggregate]:
        """Get daily aggregates for uptime calculation."""
        conn = await self._get_connection()
        
        conditions = []
        params = []
        
        if component is not None:
            conditions.append("component = ?")
            params.append(component)
            
        if start_date is not None:
            conditions.append("date >= ?")
            params.append(start_date.isoformat())
            
        if end_date is not None:
            conditions.append("date <= ?")
            params.append(end_date.isoformat())
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cursor = await conn.execute(
            f"""
            SELECT id, date, component, healthy_seconds, degraded_seconds,
                   unhealthy_seconds, unreachable_seconds, incident_count, created_at
            FROM daily_aggregates
            WHERE {where_clause}
            ORDER BY date DESC, component ASC
            """,
            params,
        )
        rows = await cursor.fetchall()
        
        return [
            DailyAggregate(
                id=row[0],
                date=row[1],
                component=row[2],
                healthy_seconds=row[3],
                degraded_seconds=row[4],
                unhealthy_seconds=row[5],
                unreachable_seconds=row[6],
                incident_count=row[7],
                created_at=self._iso_to_datetime(row[8]) if row[8] else None,
            )
            for row in rows
        ]

    async def cleanup_old_data(
        self,
        snapshots_days: int,
        incidents_days: int,
        aggregates_days: int,
    ) -> Dict[str, int]:
        """Delete data older than retention periods."""
        conn = await self._get_connection()
        now = datetime.now(timezone.utc)
        
        deleted = {}
        
        # Delete old snapshots
        cutoff = now - timedelta(days=snapshots_days)
        cursor = await conn.execute(
            "DELETE FROM health_snapshots WHERE timestamp < ?",
            (self._datetime_to_iso(cutoff),),
        )
        deleted["health_snapshots"] = cursor.rowcount
        
        # Delete old incidents
        cutoff = now - timedelta(days=incidents_days)
        cursor = await conn.execute(
            "DELETE FROM incidents WHERE timestamp < ?",
            (self._datetime_to_iso(cutoff),),
        )
        deleted["incidents"] = cursor.rowcount
        
        # Delete old aggregates
        cutoff_date = (now - timedelta(days=aggregates_days)).date()
        cursor = await conn.execute(
            "DELETE FROM daily_aggregates WHERE date < ?",
            (cutoff_date.isoformat(),),
        )
        deleted["daily_aggregates"] = cursor.rowcount
        
        await conn.commit()
        
        total = sum(deleted.values())
        if total > 0:
            self._log_info(
                f"🗑️ Cleanup complete: {deleted['health_snapshots']} snapshots, "
                f"{deleted['incidents']} incidents, {deleted['daily_aggregates']} aggregates deleted"
            )
        else:
            self._log_debug("🗑️ Cleanup complete: no old data to delete")
            
        return deleted

    async def get_snapshot_count(self, since: Optional[datetime] = None) -> int:
        """Get count of snapshots."""
        conn = await self._get_connection()
        
        if since is not None:
            cursor = await conn.execute(
                "SELECT COUNT(*) FROM health_snapshots WHERE timestamp >= ?",
                (self._datetime_to_iso(since),),
            )
        else:
            cursor = await conn.execute("SELECT COUNT(*) FROM health_snapshots")
            
        row = await cursor.fetchone()
        return row[0] if row else 0

    async def close(self) -> None:
        """Close database connection."""
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
            self._log_info("🔌 Metrics database connection closed")


# =============================================================================
# Factory Function (Clean Architecture Rule #1)
# =============================================================================
def create_metrics_database(
    db_path: str,
    logger: Optional[LoggingConfigManager] = None,
) -> SQLiteMetricsDatabase:
    """
    Factory function to create a metrics database instance.
    
    Args:
        db_path: Path to the SQLite database file
        logger: Optional logging manager instance
        
    Returns:
        SQLiteMetricsDatabase instance
        
    Note:
        Call initialize() on the returned instance to set up the schema.
    """
    return SQLiteMetricsDatabase(db_path=db_path, logger=logger)


__all__ = [
    # Data classes
    "HealthSnapshot",
    "Incident",
    "DailyAggregate",
    "UptimeMetrics",
    # Interface
    "MetricsDatabaseInterface",
    # Implementation
    "SQLiteMetricsDatabase",
    # Factory
    "create_metrics_database",
    # Constants
    "CURRENT_SCHEMA_VERSION",
]
