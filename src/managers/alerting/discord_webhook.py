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
Discord Webhook - Send Rich Embed Alerts to Discord Channels
----------------------------------------------------------------------------
FILE VERSION: v5.0-4-2.0-1
LAST MODIFIED: 2026-01-17
PHASE: Phase 4 - Alerting Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash
============================================================================
"""

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from src.managers.alerting.alert_manager import AlertType, StatusTransition
from src.managers.logging_manager import LoggingConfigManager


# =============================================================================
# Constants
# =============================================================================
# Discord embed colors (decimal values)
COLORS = {
    AlertType.CRITICAL: 0xFF0000,  # Red
    AlertType.WARNING: 0xFFAA00,   # Orange/Yellow
    AlertType.RECOVERY: 0x00FF00,  # Green
    AlertType.INFO: 0x0099FF,      # Blue
}

# Discord embed emojis
EMOJIS = {
    AlertType.CRITICAL: "🔴",
    AlertType.WARNING: "⚠️",
    AlertType.RECOVERY: "🟢",
    AlertType.INFO: "ℹ️",
}

# Component display names
COMPONENT_NAMES = {
    "ash_bot": "Ash-Bot",
    "ash_nlp": "Ash-NLP",
    "ash_dash": "Ash-Dash",
    "ash_vault": "Ash-Vault",
    "ash_thrash": "Ash-Thrash",
    "ash": "Ash (Core)",
}

# Docker secrets path
SECRETS_PATH = Path("/run/secrets")


# =============================================================================
# Webhook URL Loader
# =============================================================================
def load_webhook_url(secret_name: str = "ash_discord_alert_token") -> Optional[str]:
    """
    Load the Discord webhook URL from Docker secrets.

    Args:
        secret_name: Name of the secret file containing the webhook URL

    Returns:
        Webhook URL string, or None if not found
    """
    # Try Docker secrets path first
    secret_path = SECRETS_PATH / secret_name
    if secret_path.exists():
        try:
            return secret_path.read_text().strip()
        except Exception:
            pass

    # Fallback to local secrets directory (development)
    local_secret = Path("secrets") / secret_name
    if local_secret.exists():
        try:
            return local_secret.read_text().strip()
        except Exception:
            pass

    return None


# =============================================================================
# Discord Webhook Sender
# =============================================================================
class DiscordWebhookSender:
    """
    Sends alert notifications to Discord via webhooks.

    Features:
        - Rich embed formatting with colors and emojis
        - Retry logic with exponential backoff
        - Rate limit handling
        - Graceful error handling
    """

    # Retry configuration
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 1.0  # seconds
    TIMEOUT_SECONDS = 10.0

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        logger: Optional[LoggingConfigManager] = None,
    ):
        """
        Initialize the Discord webhook sender.

        Args:
            webhook_url: Discord webhook URL (loaded from secrets if not provided)
            logger: Optional logging manager instance
        """
        self._webhook_url = webhook_url or load_webhook_url()
        self._logger = logger
        self._log = logger.get_logger("discord_webhook") if logger else None

        if self._webhook_url:
            self._log_info("✅ Discord webhook configured")
        else:
            self._log_warning("⚠️ No Discord webhook URL configured - alerts disabled")

    def _log_info(self, message: str) -> None:
        """Log info message if logger is available."""
        if self._log:
            self._log.info(message)

    def _log_warning(self, message: str) -> None:
        """Log warning message if logger is available."""
        if self._log:
            self._log.warning(message)

    def _log_error(self, message: str) -> None:
        """Log error message if logger is available."""
        if self._log:
            self._log.error(message)

    def _log_debug(self, message: str) -> None:
        """Log debug message if logger is available."""
        if self._log:
            self._log.debug(message)

    @property
    def is_configured(self) -> bool:
        """Check if the webhook is properly configured."""
        return self._webhook_url is not None and self._webhook_url.startswith("https://")

    async def send_alert(self, transition: StatusTransition) -> bool:
        """
        Send an alert for a status transition to Discord.

        Args:
            transition: The status transition to alert on

        Returns:
            True if alert was sent successfully, False otherwise
        """
        if not self.is_configured:
            self._log_warning("Cannot send alert - webhook not configured")
            return False

        # Build the embed
        embed = self._build_embed(transition)
        payload = {"embeds": [embed]}

        # Send with retry logic
        return await self._send_with_retry(payload)

    def _build_embed(self, transition: StatusTransition) -> Dict[str, Any]:
        """
        Build a Discord embed for a status transition.

        Args:
            transition: The status transition

        Returns:
            Discord embed dictionary
        """
        alert_type = transition.alert_type
        emoji = EMOJIS.get(alert_type, "📢")
        color = COLORS.get(alert_type, 0x808080)

        # Get display name for the entity
        display_name = self._get_display_name(transition.entity_name)

        # Build title based on alert type
        if alert_type == AlertType.RECOVERY:
            title = f"{emoji} {display_name} Recovered"
        else:
            title = f"{emoji} {display_name} Status Change"

        # Build description
        description = (
            f"Status changed from **{transition.from_status.value}** to "
            f"**{transition.to_status.value}**"
        )

        # Build fields
        fields = [
            {
                "name": "Component",
                "value": display_name,
                "inline": True,
            },
            {
                "name": "New Status",
                "value": transition.to_status.value.upper(),
                "inline": True,
            },
            {
                "name": "Time",
                "value": f"<t:{int(transition.timestamp.timestamp())}:R>",
                "inline": True,
            },
        ]

        # Add downtime field for recovery alerts
        if transition.is_recovery and "downtime_formatted" in transition.details:
            fields.append({
                "name": "Downtime",
                "value": transition.details["downtime_formatted"],
                "inline": True,
            })

        # Add error field if present
        if transition.error:
            fields.append({
                "name": "Error",
                "value": f"```{transition.error[:200]}```",
                "inline": False,
            })

        # Add latency field if present (for connection alerts)
        if "latency_ms" in transition.details:
            fields.append({
                "name": "Latency",
                "value": f"{transition.details['latency_ms']}ms",
                "inline": True,
            })

        embed = {
            "title": title,
            "description": description,
            "color": color,
            "fields": fields,
            "footer": {
                "text": "Ash Ecosystem Health Monitor",
            },
            "timestamp": transition.timestamp.isoformat(),
        }

        return embed

    def _get_display_name(self, entity_name: str) -> str:
        """
        Get a human-readable display name for an entity.

        Args:
            entity_name: Internal entity name

        Returns:
            Display name
        """
        # Check component names mapping
        if entity_name in COMPONENT_NAMES:
            return COMPONENT_NAMES[entity_name]

        # Handle connection names (e.g., "ash-bot -> ash-nlp")
        if " -> " in entity_name:
            return entity_name  # Already readable

        # Capitalize and replace underscores
        return entity_name.replace("_", "-").title()

    async def _send_with_retry(self, payload: Dict[str, Any]) -> bool:
        """
        Send payload to Discord webhook with retry logic.

        Args:
            payload: The webhook payload to send

        Returns:
            True if successful, False otherwise
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=self.TIMEOUT_SECONDS) as client:
                    response = await client.post(
                        self._webhook_url,
                        json=payload,
                    )

                    # Success (204 No Content is expected)
                    if response.status_code in (200, 204):
                        self._log_debug("✅ Discord alert sent successfully")
                        return True

                    # Rate limited
                    if response.status_code == 429:
                        retry_after = response.json().get("retry_after", 5)
                        self._log_warning(
                            f"⏳ Discord rate limited, waiting {retry_after}s..."
                        )
                        await asyncio.sleep(retry_after)
                        continue

                    # Other error
                    self._log_error(
                        f"❌ Discord webhook error: HTTP {response.status_code}"
                    )

            except httpx.TimeoutException:
                self._log_warning(f"⏱️ Discord webhook timeout (attempt {attempt + 1})")

            except Exception as e:
                self._log_error(f"❌ Discord webhook error: {e}")

            # Exponential backoff before retry
            if attempt < self.MAX_RETRIES - 1:
                delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                self._log_debug(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)

        self._log_error(f"❌ Failed to send Discord alert after {self.MAX_RETRIES} attempts")
        return False

    async def send_ecosystem_summary(
        self,
        transitions: list,
        ecosystem_status: str,
    ) -> bool:
        """
        Send a summary alert for multiple transitions (batch notification).

        Useful when multiple components change status simultaneously.

        Args:
            transitions: List of StatusTransition objects
            ecosystem_status: Current ecosystem status

        Returns:
            True if alert was sent successfully, False otherwise
        """
        if not self.is_configured:
            return False

        if not transitions:
            return True

        # Determine severity based on transitions
        has_critical = any(t.is_critical for t in transitions)
        has_recovery = any(t.is_recovery for t in transitions)

        if has_critical:
            color = COLORS[AlertType.CRITICAL]
            emoji = EMOJIS[AlertType.CRITICAL]
            title = f"{emoji} Ecosystem Alert: Multiple Issues Detected"
        elif has_recovery:
            color = COLORS[AlertType.RECOVERY]
            emoji = EMOJIS[AlertType.RECOVERY]
            title = f"{emoji} Ecosystem Alert: Services Recovering"
        else:
            color = COLORS[AlertType.WARNING]
            emoji = EMOJIS[AlertType.WARNING]
            title = f"{emoji} Ecosystem Alert: Status Changes"

        # Build summary description
        description_lines = []
        for t in transitions:
            t_emoji = EMOJIS.get(t.alert_type, "•")
            display_name = self._get_display_name(t.entity_name)
            description_lines.append(
                f"{t_emoji} **{display_name}**: {t.from_status.value} → {t.to_status.value}"
            )

        embed = {
            "title": title,
            "description": "\n".join(description_lines),
            "color": color,
            "fields": [
                {
                    "name": "Ecosystem Status",
                    "value": ecosystem_status.upper(),
                    "inline": True,
                },
                {
                    "name": "Components Affected",
                    "value": str(len(transitions)),
                    "inline": True,
                },
                {
                    "name": "Time",
                    "value": f"<t:{int(datetime.now(timezone.utc).timestamp())}:R>",
                    "inline": True,
                },
            ],
            "footer": {
                "text": "Ash Ecosystem Health Monitor",
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        payload = {"embeds": [embed]}
        return await self._send_with_retry(payload)


# =============================================================================
# Factory Function (Clean Architecture Rule #1)
# =============================================================================
def create_discord_webhook_sender(
    webhook_url: Optional[str] = None,
    logger: Optional[LoggingConfigManager] = None,
) -> DiscordWebhookSender:
    """
    Factory function to create a DiscordWebhookSender instance.

    Args:
        webhook_url: Discord webhook URL (loaded from secrets if not provided)
        logger: Optional logging manager instance

    Returns:
        Configured DiscordWebhookSender instance
    """
    return DiscordWebhookSender(
        webhook_url=webhook_url,
        logger=logger,
    )


__all__ = [
    "DiscordWebhookSender",
    "create_discord_webhook_sender",
    "load_webhook_url",
]
