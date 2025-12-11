"""Pushover notification handler for stargazing conditions."""

import logging
from typing import Dict, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ServiceDataType

_LOGGER = logging.getLogger(__name__)


class StargazingNotificationService:
    """Handle sending notifications via Pushover."""

    def __init__(self, hass: HomeAssistant, notify_service: str):
        """Initialize notification service.

        Args:
            hass: Home Assistant instance
            notify_service: Service name (e.g., "notify.mandalore")
        """
        self.hass = hass
        self.notify_service = notify_service
        self.last_exceptional_notification = None
        self.last_amazing_notification = None

    async def send_test_notification(self) -> bool:
        """Send a test notification to verify Pushover is working.

        Returns:
            True if successful, False otherwise
        """
        try:
            await self.hass.services.async_call(
                "notify",
                self.notify_service.split(".")[-1],
                {
                    "title": "🌟 Stargazing Integration Test",
                    "message": "Test notification successful! Integration is ready.",
                    "priority": 0,
                },
            )
            _LOGGER.info("Test notification sent successfully")
            return True
        except Exception as e:
            _LOGGER.error(f"Failed to send test notification: {e}")
            return False

    async def send_exceptional_alert(
        self, score: int, breakdown: Dict, optimal_window: Dict
    ) -> bool:
        """Send notification for exceptional stargazing conditions (score ≥90).

        Args:
            score: Quality score (0-100)
            breakdown: Component breakdown dict
            optimal_window: Dict with start/end times

        Returns:
            True if sent successfully
        """
        try:
            cloudless = breakdown.get("cloudless", {}).get("value", 0)
            transparency = breakdown.get("transparency", {}).get("value", 0)
            seeing = breakdown.get("seeing", {}).get("value", 0)

            message = (
                f"PERFECT CONDITIONS DETECTED!\n"
                f"Score: {score}/100\n\n"
                f"Sky Clarity: {cloudless:.0f}%\n"
                f"Transparency: {transparency:.0f}%\n"
                f"Seeing: {seeing:.0f}%\n\n"
                f"🔭 Get outside NOW!\n"
                f"Optimal: {optimal_window.get('start', 'N/A')} - "
                f"{optimal_window.get('end', 'N/A')}"
            )

            await self.hass.services.async_call(
                "notify",
                self.notify_service.split(".")[-1],
                {
                    "title": "⭐ EXCEPTIONAL STARGAZING NOW",
                    "message": message,
                    "priority": 1,  # High priority
                    "sound": "echo",
                },
            )
            _LOGGER.info(f"Exceptional alert sent (score={score})")
            return True
        except Exception as e:
            _LOGGER.error(f"Failed to send exceptional alert: {e}")
            return False

    async def send_amazing_conditions_alert(
        self, score: int, breakdown: Dict, optimal_window: Dict
    ) -> bool:
        """Send notification for amazing stargazing conditions (score 80-89).

        Args:
            score: Quality score (0-100)
            breakdown: Component breakdown dict
            optimal_window: Dict with start/end times

        Returns:
            True if sent successfully
        """
        try:
            cloudless = breakdown.get("cloudless", {}).get("value", 0)
            transparency = breakdown.get("transparency", {}).get("value", 0)
            seeing = breakdown.get("seeing", {}).get("value", 0)
            moon_phase = breakdown.get("moon_phase", {}).get("value", 0)

            moon_note = (
                f"\n🌙 Moon Phase: {moon_phase:.0f}%"
                if moon_phase > 10 and moon_phase < 90
                else ""
            )

            message = (
                f"Great stargazing conditions tonight!\n"
                f"Score: {score}/100\n\n"
                f"Sky Clarity: {cloudless:.0f}%\n"
                f"Transparency: {transparency:.0f}%\n"
                f"Seeing: {seeing:.0f}%{moon_note}\n\n"
                f"Best viewing: {optimal_window.get('start', 'N/A')} - "
                f"{optimal_window.get('end', 'N/A')}"
            )

            await self.hass.services.async_call(
                "notify",
                self.notify_service.split(".")[-1],
                {
                    "title": "🌟 AMAZING STARS TONIGHT",
                    "message": message,
                    "priority": 0,  # Normal priority
                },
            )
            _LOGGER.info(f"Amazing conditions alert sent (score={score})")
            return True
        except Exception as e:
            _LOGGER.error(f"Failed to send amazing conditions alert: {e}")
            return False

    async def send_astronomy_event_alert(self, event_data: Dict) -> bool:
        """Send notification about upcoming astronomy event.

        Args:
            event_data: Event dict with name, description, time, etc.

        Returns:
            True if sent successfully
        """
        try:
            message = (
                f"{event_data.get('name', 'Astronomy Event')}\n\n"
                f"{event_data.get('description', 'Check the skies!')}\n\n"
                f"When: {event_data.get('time', 'Tonight')}"
            )

            await self.hass.services.async_call(
                "notify",
                self.notify_service.split(".")[-1],
                {
                    "title": f"🌠 {event_data.get('name', 'Astronomy Event')}",
                    "message": message,
                    "priority": 0,
                },
            )
            _LOGGER.info(f"Event alert sent: {event_data.get('name', 'Unknown')}")
            return True
        except Exception as e:
            _LOGGER.error(f"Failed to send event alert: {e}")
            return False

    async def send_poor_conditions_info(self, reason: str) -> bool:
        """Send informational message about why conditions are poor.

        Args:
            reason: Explanation of poor conditions

        Returns:
            True if sent successfully
        """
        try:
            await self.hass.services.async_call(
                "notify",
                self.notify_service.split(".")[-1],
                {
                    "title": "🌫️ Stargazing Not Recommended",
                    "message": f"{reason}\n\nCheck back tomorrow!",
                    "priority": -1,  # Low priority
                },
            )
            _LOGGER.info(f"Poor conditions info sent: {reason}")
            return True
        except Exception as e:
            _LOGGER.error(f"Failed to send poor conditions info: {e}")
            return False
