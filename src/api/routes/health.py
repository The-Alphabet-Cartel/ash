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
Health Routes - API Endpoints for Health Monitoring
----------------------------------------------------------------------------
FILE VERSION: v5.0-1-1.4-1
LAST MODIFIED: 2026-01-15
PHASE: Phase 1 - Ecosystem Health API
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================
"""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse

from src.managers.ecosystem.ecosystem_health_manager import (
    ComponentStatus,
    EcosystemHealthManager,
)


# =============================================================================
# Router Setup
# =============================================================================
router = APIRouter(tags=["Health"])


# =============================================================================
# Dependency Injection Helper
# =============================================================================
def get_ecosystem_manager(request: Request) -> EcosystemHealthManager:
    """Get the EcosystemHealthManager from app state."""
    return request.app.state.ecosystem_manager


# =============================================================================
# Root Endpoint
# =============================================================================
@router.get(
    "/",
    summary="Service Information",
    description="Returns information about the Ash Ecosystem Health API and available endpoints.",
    response_model=Dict[str, Any],
)
async def root() -> Dict[str, Any]:
    """
    Service information endpoint.

    Returns basic information about the service and available endpoints.
    """
    return {
        "service": "Ash Ecosystem Health API",
        "description": "Centralized health monitoring for the Ash Crisis Detection Ecosystem",
        "version": "v5.0-1",
        "community": {
            "name": "The Alphabet Cartel",
            "discord": "https://discord.gg/alphabetcartel",
            "website": "https://alphabetcartel.org",
        },
        "endpoints": {
            "/": "This endpoint - service information",
            "/health": "Liveness probe - is the service running?",
            "/health/ready": "Readiness probe - is the service ready to serve?",
            "/health/ecosystem": "Full ecosystem health report",
        },
        "documentation": "/docs",
    }


# =============================================================================
# Liveness Probe
# =============================================================================
@router.get(
    "/health",
    summary="Liveness Probe",
    description="Simple liveness check - returns 200 if the service is running.",
    response_model=Dict[str, Any],
)
async def health_liveness() -> Dict[str, Any]:
    """
    Liveness probe endpoint.

    Returns 200 OK if the service is running. Used by container orchestrators
    (Docker, Kubernetes) to determine if the service should be restarted.
    """
    return {
        "status": "healthy",
        "service": "ash-ecosystem-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Kubernetes-style alias
@router.get(
    "/healthz",
    summary="Liveness Probe (K8s alias)",
    description="Kubernetes-style liveness probe alias.",
    include_in_schema=False,
)
async def health_liveness_k8s() -> Dict[str, Any]:
    """Kubernetes-style liveness probe alias."""
    return await health_liveness()


# =============================================================================
# Readiness Probe
# =============================================================================
@router.get(
    "/health/ready",
    summary="Readiness Probe",
    description="Readiness check - returns 200 if the service is ready to accept requests.",
    response_model=Dict[str, Any],
)
async def health_readiness(
    request: Request,
) -> Dict[str, Any]:
    """
    Readiness probe endpoint.

    Returns 200 OK if the service is ready to accept requests.
    Checks that all required dependencies are available.
    """
    # Check that we have a valid ecosystem manager
    try:
        manager = request.app.state.ecosystem_manager
        if manager is None:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": "Ecosystem manager not initialized",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
    except AttributeError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": "Service not fully initialized",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    return {
        "status": "healthy",
        "ready": True,
        "service": "ash-ecosystem-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Kubernetes-style alias
@router.get(
    "/readyz",
    summary="Readiness Probe (K8s alias)",
    description="Kubernetes-style readiness probe alias.",
    include_in_schema=False,
)
async def health_readiness_k8s(request: Request) -> Dict[str, Any]:
    """Kubernetes-style readiness probe alias."""
    return await health_readiness(request)


# =============================================================================
# Ecosystem Health (Main Feature)
# =============================================================================
@router.get(
    "/health/ecosystem",
    summary="Ecosystem Health Report",
    description=(
        "Performs health checks on all Ash ecosystem components and returns "
        "an aggregated report including component status, connection health, "
        "and overall ecosystem status."
    ),
    response_model=Dict[str, Any],
    responses={
        200: {
            "description": "Ecosystem is healthy or degraded",
            "content": {
                "application/json": {
                    "example": {
                        "ecosystem": "ash",
                        "status": "healthy",
                        "timestamp": "2026-01-15T19:42:31Z",
                        "summary": {
                            "healthy": 4,
                            "degraded": 0,
                            "unhealthy": 0,
                            "unreachable": 0,
                            "disabled": 1,
                        },
                        "components": {
                            "ash_bot": {
                                "status": "healthy",
                                "response_time_ms": 12,
                            }
                        },
                        "connections": {
                            "ash-bot -> ash-nlp": {
                                "status": "healthy",
                                "latency_ms": 23,
                            }
                        },
                        "meta": {
                            "check_duration_ms": 312,
                            "timeout_ms": 5000,
                        },
                    }
                }
            },
        },
        503: {
            "description": "Ecosystem has unhealthy or unreachable components",
        },
    },
)
async def health_ecosystem(
    response: Response,
    manager: EcosystemHealthManager = Depends(get_ecosystem_manager),
) -> Dict[str, Any]:
    """
    Full ecosystem health check endpoint.

    Performs parallel health checks on all configured Ash components,
    validates inter-component connections, and returns an aggregated
    health report.

    Returns:
        200: If ecosystem is healthy or degraded
        503: If ecosystem has unhealthy or unreachable components
    """
    # Perform the ecosystem health check
    health = await manager.check_ecosystem_health()

    # Set appropriate HTTP status code based on ecosystem status
    if health.status in (ComponentStatus.UNHEALTHY, ComponentStatus.UNREACHABLE):
        response.status_code = 503

    return health.to_dict()


__all__ = ["router"]
