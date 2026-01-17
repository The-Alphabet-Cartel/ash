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
Alerting Package - Discord Webhook Alerting for Ecosystem Health Changes
----------------------------------------------------------------------------
FILE VERSION: v5.0-4-2.0-1
LAST MODIFIED: 2026-01-17
PHASE: Phase 4 - Alerting Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================
"""

from src.managers.alerting.alert_manager import (
    AlertManager,
    AlertState,
    AlertType,
    StatusTransition,
    create_alert_manager,
)
from src.managers.alerting.discord_webhook import (
    DiscordWebhookSender,
    create_discord_webhook_sender,
    load_webhook_url,
)

__all__ = [
    # Alert Manager
    "AlertManager",
    "AlertState",
    "AlertType",
    "StatusTransition",
    "create_alert_manager",
    # Discord Webhook
    "DiscordWebhookSender",
    "create_discord_webhook_sender",
    "load_webhook_url",
]
