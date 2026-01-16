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
Main Application - FastAPI Entry Point for Ash Ecosystem Health API
----------------------------------------------------------------------------
FILE VERSION: v5.0-1-1.5-1
LAST MODIFIED: 2026-01-15
PHASE: Phase 1 - Ecosystem Health API
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.managers.config_manager import create_config_manager
from src.managers.logging_manager import create_logging_manager
from src.managers.ecosystem.ecosystem_health_manager import (
    create_ecosystem_health_manager,
)
from src.api.routes.health import router as health_router


# =============================================================================
# Application Version
# =============================================================================
__version__ = "5.0.0"


# =============================================================================
# Lifespan Context Manager
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown tasks:
        - Startup: Initialize configuration, logging, and managers
        - Shutdown: Cleanup resources
    """
    # =========================================================================
    # STARTUP
    # =========================================================================

    # Initialize logging first (with bootstrap defaults)
    bootstrap_logger = create_logging_manager(
        level="INFO",
        log_format="human",
        app_name="ash",
    )
    log = bootstrap_logger.get_logger("main")

    log.info("=" * 70)
    log.info("🌳 Ash Ecosystem Health API - Starting Up")
    log.info("=" * 70)

    # Load configuration
    log.info("📋 Loading configuration...")
    config_manager = create_config_manager(logger=bootstrap_logger)

    # Reconfigure logging with loaded settings
    logger = create_logging_manager(
        level=config_manager.log_level,
        log_format=config_manager.log_format,
        log_file=config_manager.log_file,
        console_enabled=config_manager.log_console,
        app_name="ash",
    )
    log = logger.get_logger("main")

    log.info(f"🔧 Environment: {config_manager.environment}")
    log.info(f"🔧 Log Level: {config_manager.log_level}")

    # Initialize the Ecosystem Health Manager
    log.info("🏥 Initializing Ecosystem Health Manager...")
    ecosystem_manager = create_ecosystem_health_manager(
        config_manager=config_manager,
        logger=logger,
    )

    # Store managers in app state for dependency injection
    app.state.config_manager = config_manager
    app.state.logger = logger
    app.state.ecosystem_manager = ecosystem_manager

    log.info("=" * 70)
    log.info("✅ Ash Ecosystem Health API - Ready")
    log.info(f"🌐 Listening on {config_manager.server_host}:{config_manager.server_port}")
    log.info("=" * 70)

    # Yield control to the application
    yield

    # =========================================================================
    # SHUTDOWN
    # =========================================================================
    log.info("=" * 70)
    log.info("🛑 Ash Ecosystem Health API - Shutting Down")
    log.info("=" * 70)

    # Cleanup (if needed in future phases)
    log.info("✅ Shutdown complete")


# =============================================================================
# Create FastAPI Application
# =============================================================================
def create_app() -> FastAPI:
    """
    Factory function to create the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="Ash Ecosystem Health API",
        description=(
            "Centralized health monitoring for the Ash Crisis Detection Ecosystem. "
            "Provides aggregated health status for all Ash components and validates "
            "inter-component connectivity.\n\n"
            "**Community**: [The Alphabet Cartel](https://discord.gg/alphabetcartel) | "
            "[alphabetcartel.org](https://alphabetcartel.org)\n\n"
            "**Repository**: [github.com/the-alphabet-cartel/ash](https://github.com/the-alphabet-cartel/ash)"
        ),
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # =========================================================================
    # CORS Middleware
    # =========================================================================
    # Allow Ash-Dash and other internal services to access the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://crt.alphabetcartel.net",  # Ash-Dash production
            "http://localhost:3000",            # Ash-Dash development
            "http://localhost:5173",            # Vite dev server
        ],
        allow_credentials=True,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["*"],
    )

    # =========================================================================
    # Include Routers
    # =========================================================================
    app.include_router(health_router)

    return app


# =============================================================================
# Application Instance
# =============================================================================
app = create_app()


# =============================================================================
# CLI Entry Point (for direct execution)
# =============================================================================
if __name__ == "__main__":
    import uvicorn

    # Load config to get host/port (bootstrap)
    config = create_config_manager()

    uvicorn.run(
        "main:app",
        host=config.server_host,
        port=config.server_port,
        reload=False,
        log_level="info",
    )
