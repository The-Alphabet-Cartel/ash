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
Metrics API Routes - Historical Health Data Endpoints
----------------------------------------------------------------------------
FILE VERSION: v5.0-5-4.0-1
LAST MODIFIED: 2026-01-17
PHASE: Phase 5 - Metrics & History
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request


router = APIRouter(prefix="/metrics", tags=["Metrics"])


# =============================================================================
# Dependency: Get Metrics Manager
# =============================================================================
async def get_metrics_manager(request: Request):
    """Dependency to get the MetricsManager from app state."""
    metrics_manager = getattr(request.app.state, "metrics_manager", None)
    if metrics_manager is None:
        raise HTTPException(
            status_code=503,
            detail="Metrics collection is not enabled or not initialized",
        )
    return metrics_manager


# =============================================================================
# Uptime Endpoints
# =============================================================================
@router.get("/uptime")
async def get_uptime(
    component: Optional[str] = Query(
        default=None,
        description="Filter to specific component (e.g., 'ash_bot')",
    ),
    days: int = Query(
        default=30,
        ge=1,
        le=90,
        description="Number of days to calculate uptime for",
    ),
    metrics_manager=Depends(get_metrics_manager),
) -> Dict[str, Any]:
    """
    Get uptime metrics for all or specific components.

    Returns uptime percentages, incident counts, and Mean Time To Recovery (MTTR)
    for the specified time period.
    """
    uptime_data = await metrics_manager.get_uptime(
        component=component,
        days=days,
    )

    # Calculate period boundaries
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    # Build response
    components = {}
    ecosystem_stats = {
        "total_healthy_seconds": 0,
        "total_degraded_seconds": 0,
        "total_unhealthy_seconds": 0,
        "total_unreachable_seconds": 0,
        "total_seconds": 0,
        "total_incidents": 0,
    }

    for comp_name, metrics in uptime_data.items():
        components[comp_name] = {
            "uptime_percentage": round(metrics.uptime_percentage, 2),
            "healthy_percentage": round(metrics.healthy_percentage, 2),
            "degraded_percentage": round(metrics.degraded_percentage, 2),
            "incident_count": metrics.incident_count,
            "mttr_seconds": metrics.mttr_seconds,
        }

        # Aggregate for ecosystem stats
        ecosystem_stats["total_healthy_seconds"] += metrics.healthy_seconds
        ecosystem_stats["total_degraded_seconds"] += metrics.degraded_seconds
        ecosystem_stats["total_unhealthy_seconds"] += metrics.unhealthy_seconds
        ecosystem_stats["total_unreachable_seconds"] += metrics.unreachable_seconds
        ecosystem_stats["total_seconds"] += metrics.total_seconds
        ecosystem_stats["total_incidents"] += metrics.incident_count

    # Calculate ecosystem-wide uptime
    total = ecosystem_stats["total_seconds"]
    if total > 0:
        healthy = ecosystem_stats["total_healthy_seconds"]
        degraded = ecosystem_stats["total_degraded_seconds"]
        ecosystem_uptime = ((healthy + degraded) / total) * 100
        ecosystem_healthy = (healthy / total) * 100
        ecosystem_degraded = (degraded / total) * 100
    else:
        ecosystem_uptime = 100.0
        ecosystem_healthy = 100.0
        ecosystem_degraded = 0.0

    return {
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "days": days,
        },
        "ecosystem": {
            "uptime_percentage": round(ecosystem_uptime, 2),
            "healthy_percentage": round(ecosystem_healthy, 2),
            "degraded_percentage": round(ecosystem_degraded, 2),
            "incident_count": ecosystem_stats["total_incidents"],
        },
        "components": components,
    }


@router.get("/uptime/{component}")
async def get_component_uptime(
    component: str,
    days: int = Query(
        default=30,
        ge=1,
        le=90,
        description="Number of days to calculate uptime for",
    ),
    metrics_manager=Depends(get_metrics_manager),
) -> Dict[str, Any]:
    """
    Get detailed uptime metrics for a specific component.
    """
    uptime_data = await metrics_manager.get_uptime(
        component=component,
        days=days,
    )

    if component not in uptime_data:
        raise HTTPException(
            status_code=404,
            detail=f"No metrics found for component: {component}",
        )

    metrics = uptime_data[component]
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    return {
        "component": component,
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "days": days,
        },
        "metrics": {
            "uptime_percentage": round(metrics.uptime_percentage, 2),
            "healthy_percentage": round(metrics.healthy_percentage, 2),
            "degraded_percentage": round(metrics.degraded_percentage, 2),
            "total_seconds": metrics.total_seconds,
            "healthy_seconds": metrics.healthy_seconds,
            "degraded_seconds": metrics.degraded_seconds,
            "unhealthy_seconds": metrics.unhealthy_seconds,
            "unreachable_seconds": metrics.unreachable_seconds,
            "incident_count": metrics.incident_count,
            "mttr_seconds": metrics.mttr_seconds,
        },
    }


# =============================================================================
# Incidents Endpoints
# =============================================================================
@router.get("/incidents")
async def get_incidents(
    component: Optional[str] = Query(
        default=None,
        description="Filter to specific component",
    ),
    days: int = Query(
        default=30,
        ge=1,
        le=90,
        description="Number of days of history",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Maximum number of incidents to return",
    ),
    metrics_manager=Depends(get_metrics_manager),
) -> Dict[str, Any]:
    """
    Get incident history.

    Returns a list of status transition events for the specified time period.
    """
    incidents = await metrics_manager.get_incidents(
        component=component,
        days=days,
        limit=limit,
    )

    # Calculate period boundaries
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    return {
        "incidents": [
            {
                "id": inc.id,
                "timestamp": inc.timestamp.isoformat(),
                "entity_type": inc.entity_type,
                "entity_name": inc.entity_name,
                "from_status": inc.from_status,
                "to_status": inc.to_status,
                "resolved_at": inc.resolved_at.isoformat() if inc.resolved_at else None,
                "duration_seconds": inc.duration_seconds,
                "error_message": inc.error_message,
            }
            for inc in incidents
        ],
        "total": len(incidents),
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "days": days,
        },
    }


# =============================================================================
# History Endpoints
# =============================================================================
@router.get("/history")
async def get_health_history(
    hours: int = Query(
        default=24,
        ge=1,
        le=168,
        description="Number of hours of history",
    ),
    resolution: str = Query(
        default="5m",
        pattern="^(1m|5m|15m|1h)$",
        description="Resolution for downsampling (1m, 5m, 15m, 1h)",
    ),
    metrics_manager=Depends(get_metrics_manager),
) -> Dict[str, Any]:
    """
    Get historical health snapshots (downsampled).

    Returns ecosystem status at regular intervals for charting/visualization.
    """
    # Calculate time range
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)

    # Get snapshots from database
    snapshots = await metrics_manager._db.get_snapshots(
        start=start,
        end=end,
        limit=10000,  # Raw limit
    )

    if not snapshots:
        return {
            "period": {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "hours": hours,
                "resolution": resolution,
            },
            "snapshots": [],
        }

    # Downsample based on resolution
    resolution_seconds = {
        "1m": 60,
        "5m": 300,
        "15m": 900,
        "1h": 3600,
    }
    interval = resolution_seconds[resolution]

    # Group snapshots by interval
    downsampled = []
    current_bucket = None
    bucket_snapshots = []

    for snapshot in sorted(snapshots, key=lambda s: s.timestamp):
        # Calculate bucket timestamp (floor to interval)
        bucket_ts = snapshot.timestamp.replace(
            second=0, microsecond=0
        )
        bucket_minutes = (bucket_ts.minute // (interval // 60)) * (interval // 60)
        bucket_ts = bucket_ts.replace(minute=bucket_minutes)

        if current_bucket is None:
            current_bucket = bucket_ts

        if bucket_ts != current_bucket:
            # Emit the bucket (use last snapshot in bucket)
            if bucket_snapshots:
                last = bucket_snapshots[-1]
                downsampled.append({
                    "timestamp": current_bucket.isoformat(),
                    "ecosystem_status": last.ecosystem_status,
                    "components": {
                        name: data.get("status", "unknown") if isinstance(data, dict) else "unknown"
                        for name, data in last.components.items()
                    },
                })
            current_bucket = bucket_ts
            bucket_snapshots = []

        bucket_snapshots.append(snapshot)

    # Don't forget the last bucket
    if bucket_snapshots:
        last = bucket_snapshots[-1]
        downsampled.append({
            "timestamp": current_bucket.isoformat(),
            "ecosystem_status": last.ecosystem_status,
            "components": {
                name: data.get("status", "unknown") if isinstance(data, dict) else "unknown"
                for name, data in last.components.items()
            },
        })

    return {
        "period": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "hours": hours,
            "resolution": resolution,
        },
        "snapshots": downsampled,
    }


# =============================================================================
# Stats Endpoint
# =============================================================================
@router.get("/stats")
async def get_metrics_stats(
    metrics_manager=Depends(get_metrics_manager),
) -> Dict[str, Any]:
    """
    Get metrics system statistics.

    Returns counts and storage information about the metrics database.
    """
    # Get counts
    total_snapshots = await metrics_manager._db.get_snapshot_count()

    last_24h = datetime.now(timezone.utc) - timedelta(hours=24)
    snapshots_24h = await metrics_manager._db.get_snapshot_count(since=last_24h)

    return {
        "snapshots": {
            "total": total_snapshots,
            "last_24h": snapshots_24h,
        },
        "retention": {
            "snapshots_days": metrics_manager._config.metrics_retention_snapshots_days,
            "incidents_days": metrics_manager._config.metrics_retention_incidents_days,
            "aggregates_days": metrics_manager._config.metrics_retention_aggregates_days,
        },
        "database": {
            "path": metrics_manager._config.metrics_db_path,
        },
    }


__all__ = ["router"]
