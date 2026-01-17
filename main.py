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
FILE VERSION: v5.0-4-3.0-1
LAST MODIFIED: 2026-01-17
PHASE: Phase 4 - Alerting Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.managers.config_manager import create_config_manager
from src.managers.logging_manager import create_logging_manager
from src.managers.ecosystem.ecosystem_health_manager import (
    EcosystemHealthManager,
    create_ecosystem_health_manager,
)
from src.managers.alerting import (
    AlertManager,
    create_alert_manager,
    create_discord_webhook_sender,
    DiscordWebhookSender,
)
from src.api.routes.health import router as health_router


# =============================================================================
# Application Version
# =============================================================================
__version__ = "5.0.1"


# =============================================================================
# Background Health Check Loop
# =============================================================================
async def health_check_loop(
    health_manager: EcosystemHealthManager,
    alert_manager: AlertManager,
    webhook_sender: DiscordWebhookSender,
    interval_seconds: int = 60,
    logger: Optional[object] = None,
) -> None:
    """
    Background task that periodically checks ecosystem health and sends alerts.

    This loop:
        1. Performs initial health check to establish baseline (no alerts)
        2. Periodically checks health at configured interval
        3. Detects status transitions and sends alerts

    Args:
        health_manager: EcosystemHealthManager instance
        alert_manager: AlertManager instance
        webhook_sender: DiscordWebhookSender instance
        interval_seconds: Seconds between health checks
        logger: Optional logger instance
    """
    log = logger.get_logger("health_loop") if logger else None

    def log_info(msg: str) -> None:
        if log:
            log.info(msg)

    def log_warning(msg: str) -> None:
        if log:
            log.warning(msg)

    def log_error(msg: str) -> None:
        if log:
            log.error(msg)

    def log_debug(msg: str) -> None:
        if log:
            log.debug(msg)

    log_info("🔄 Starting health check loop...")

    # =========================================================================
    # Initial Health Check (Establish Baseline)
    # =========================================================================
    try:
        log_info("📋 Performing initial health check to establish baseline...")
        initial_health = await health_manager.check_ecosystem_health()
        alert_manager.set_initial_state(initial_health)
        log_info(f"✅ Baseline established: ecosystem={initial_health.status.value}")
    except Exception as e:
        log_error(f"❌ Failed to establish initial state: {e}")
        # Continue anyway - will try again on next iteration
        await asyncio.sleep(interval_seconds)

    # =========================================================================
    # Main Loop
    # =========================================================================
    while True:
        try:
            # Wait for the configured interval
            await asyncio.sleep(interval_seconds)

            log_debug(f"🔍 Running periodic health check...")

            # Check ecosystem health
            current_health = await health_manager.check_ecosystem_health()

            # Detect transitions
            transitions = alert_manager.detect_transitions(current_health)

            if not transitions:
                log_debug("✅ No status transitions detected")
                continue

            # Process each transition
            alerts_sent = 0
            for transition in transitions:
                # Check cooldown
                if not alert_manager.should_alert(transition):
                    log_debug(f"⏳ Skipping alert for {transition.entity_name} (cooldown)")
                    continue

                # Send alert
                log_info(
                    f"🔔 Sending alert: {transition.entity_name} "
                    f"{transition.from_status.value} → {transition.to_status.value}"
                )

                success = await webhook_sender.send_alert(transition)

                if success:
                    alert_manager.record_alert_sent(transition)
                    alerts_sent += 1
                else:
                    log_warning(f"⚠️ Failed to send alert for {transition.entity_name}")

            if alerts_sent > 0:
                log_info(f"✅ Sent {alerts_sent} alert(s)")

        except asyncio.CancelledError:
            log_info("🛑 Health check loop cancelled")
            raise  # Re-raise to properly exit

        except Exception as e:
            log_error(f"❌ Health check loop error: {e}")
            # Continue running - don't crash the loop on errors
            await asyncio.sleep(5)  # Brief pause before retrying


# =============================================================================
# Lifespan Context Manager
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown tasks:
        - Startup: Initialize configuration, logging, managers, and background tasks
        - Shutdown: Cancel background tasks and cleanup resources
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

    # =========================================================================
    # Initialize Alerting (Phase 4)
    # =========================================================================
    health_check_task: Optional[asyncio.Task] = None

    if config_manager.alerting_enabled:
        log.info("🔔 Initializing Alerting System...")

        # Create Alert Manager
        alert_manager = create_alert_manager(
            config_manager=config_manager,
            logger=logger,
        )

        # Create Discord Webhook Sender
        webhook_sender = create_discord_webhook_sender(
            logger=logger,
        )

        if webhook_sender.is_configured:
            log.info("✅ Discord webhook configured")

            # Start background health check loop
            health_check_task = asyncio.create_task(
                health_check_loop(
                    health_manager=ecosystem_manager,
                    alert_manager=alert_manager,
                    webhook_sender=webhook_sender,
                    interval_seconds=config_manager.alerting_check_interval_seconds,
                    logger=logger,
                )
            )
            log.info(
                f"🔄 Health check loop started "
                f"(interval: {config_manager.alerting_check_interval_seconds}s, "
                f"cooldown: {config_manager.alerting_cooldown_seconds}s)"
            )

            # Store alerting components in app state
            app.state.alert_manager = alert_manager
            app.state.webhook_sender = webhook_sender
        else:
            log.warning("⚠️ Discord webhook not configured - alerting disabled")
    else:
        log.info("ℹ️ Alerting is disabled via configuration")

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

    # Cancel the health check loop if running
    if health_check_task is not None:
        log.info("🔄 Stopping health check loop...")
        health_check_task.cancel()
        try:
            await health_check_task
        except asyncio.CancelledError:
            pass
        log.info("✅ Health check loop stopped")

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
