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
Metrics Module - Historical Health Data Storage and Analysis
----------------------------------------------------------------------------
FILE VERSION: v5.0-5-2.0-1
LAST MODIFIED: 2026-01-17
PHASE: Phase 5 - Metrics & History
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================
"""

from src.managers.metrics.database import (
    # Data classes
    HealthSnapshot,
    Incident,
    DailyAggregate,
    UptimeMetrics,
    # Interface
    MetricsDatabaseInterface,
    # Implementation
    SQLiteMetricsDatabase,
    # Factory
    create_metrics_database,
    # Constants
    CURRENT_SCHEMA_VERSION,
)

from src.managers.metrics.metrics_manager import (
    MetricsManager,
    create_metrics_manager,
    EntityState,
)

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
    # Factory functions
    "create_metrics_database",
    "create_metrics_manager",
    # Manager
    "MetricsManager",
    "EntityState",
    # Constants
    "CURRENT_SCHEMA_VERSION",
]
