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
Routes Package - API Route Definitions
----------------------------------------------------------------------------
FILE VERSION: v5.0-5-4.0-1
LAST MODIFIED: 2026-01-17
PHASE: Phase 5 - Metrics & History
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================
"""

from src.api.routes.health import router as health_router
from src.api.routes.metrics import router as metrics_router

__all__ = [
    "health_router",
    "metrics_router",
]
