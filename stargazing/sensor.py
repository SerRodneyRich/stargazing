"""Stargazing sensor platform."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import STATE_UNKNOWN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import dt as dt_util

from .const import (
    ASTROWEATHER_WEATHER,
    DOMAIN,
    SENSOR_NEXT_EXCEPTIONAL,
    SENSOR_OPTIMAL_END,
    SENSOR_OPTIMAL_START,
    SENSOR_RATING,
    SENSOR_SCORE,
    SENSOR_UPCOMING_EVENTS,
    UPDATE_INTERVAL_SCORE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up Stargazing sensors."""
    try:
        _LOGGER.info("Setting up Stargazing sensor platform")

        # Get shared data
        if DOMAIN not in hass.data:
            _LOGGER.error("Stargazing data not found in hass.data")
            return

        data = hass.data[DOMAIN]

        # Create sensor entities
        entities = [
            StargazingScoreSensor(hass, data),
            StargazingRatingSensor(hass, data),
            OptimalViewingStartSensor(hass, data),
            OptimalViewingEndSensor(hass, data),
            NextExceptionalNightSensor(hass, data),
            UpcomingAstronomyEventsSensor(hass, data),
        ]

        async_add_entities(entities)
        _LOGGER.info(f"Added {len(entities)} Stargazing sensors")

        # Set up update loop
        hass.loop.create_task(_setup_update_loop(hass, data))

    except Exception as e:
        _LOGGER.error(f"Error setting up Stargazing sensors: {e}")


async def _setup_update_loop(hass: HomeAssistant, data):
    """Set up periodic update loop."""
    while True:
        try:
            await data.update_stargazing_data()

            # Check for notifications
            score = data.last_score or 0
            # Check every UPDATE_INTERVAL_SCORE seconds (60 by default)
            # Only notify if score >= 80
            if score >= 80:
                await data.check_and_notify()

            await asyncio.sleep(UPDATE_INTERVAL_SCORE)

        except Exception as e:
            _LOGGER.error(f"Error in update loop: {e}")
            await asyncio.sleep(UPDATE_INTERVAL_SCORE)


class StargazingBaseSensor(SensorEntity):
    """Base class for Stargazing sensors."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, data):
        """Initialize sensor.

        Args:
            hass: Home Assistant instance
            data: Shared StargazingData instance
        """
        self.hass = hass
        self.data = data
        self._attr_name = self.entity_description
        self._attr_unique_id = f"{DOMAIN}_{self._sensor_type}"

        # Subscribe to astroweather updates
        hass.bus.async_listen("state_changed", self._on_state_changed)

    async def _on_state_changed(self, event):
        """Handle state change events."""
        if event.data.get("entity_id") == ASTROWEATHER_WEATHER:
            # Astroweather updated, update our sensors
            await self.async_update_ha_state(force_refresh=True)


class StargazingScoreSensor(StargazingBaseSensor):
    """Sensor for stargazing quality score (0-100)."""

    _sensor_type = "quality_score"
    entity_description = "Quality Score"

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_unit_of_measurement = "%"
    _attr_icon = "mdi:star"

    @property
    def state(self) -> Optional[int]:
        """Return quality score."""
        return self.data.last_score

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        breakdown = self.data.last_score or 0
        return {
            "rating": self.data.scoring_engine.get_rating(breakdown),
            "emoji": self.data.scoring_engine.get_rating_emoji(breakdown),
            "last_updated": datetime.now().isoformat(),
        }


class StargazingRatingSensor(StargazingBaseSensor):
    """Sensor for human-readable stargazing rating."""

    _sensor_type = "rating"
    entity_description = "Rating"

    _attr_icon = "mdi:sparkles"

    @property
    def state(self) -> str:
        """Return rating."""
        if self.data.last_score is None:
            return STATE_UNKNOWN
        return self.data.scoring_engine.get_rating(self.data.last_score)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if self.data.last_score is None:
            return {}

        score = self.data.last_score
        emoji = self.data.scoring_engine.get_rating_emoji(score)
        return {
            "score": score,
            "emoji": emoji,
            "description": f"{emoji} {self.state}",
        }


class OptimalViewingStartSensor(StargazingBaseSensor):
    """Sensor for optimal viewing window start time."""

    _sensor_type = "optimal_viewing_start"
    entity_description = "Optimal Viewing Start"

    _attr_icon = "mdi:sunset-down"

    @property
    def state(self) -> str:
        """Return optimal viewing start time."""
        return STATE_UNKNOWN  # Will be updated by async_update


class OptimalViewingEndSensor(StargazingBaseSensor):
    """Sensor for optimal viewing window end time."""

    _sensor_type = "optimal_viewing_end"
    entity_description = "Optimal Viewing End"

    _attr_icon = "mdi:moon-waning-crescent"

    @property
    def state(self) -> str:
        """Return optimal viewing end time."""
        return STATE_UNKNOWN  # Will be updated by async_update


class NextExceptionalNightSensor(StargazingBaseSensor):
    """Sensor for next night with exceptional conditions (score ≥90)."""

    _sensor_type = "next_exceptional_night"
    entity_description = "Next Exceptional Night"

    _attr_icon = "mdi:calendar-star"

    @property
    def state(self) -> str:
        """Return next exceptional night."""
        # This would need historical data tracking
        # For now, return TBD
        return "TBD"

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        return {
            "note": "Requires historical tracking - coming in future update"
        }


class UpcomingAstronomyEventsSensor(StargazingBaseSensor):
    """Sensor for upcoming astronomy events."""

    _sensor_type = "upcoming_astronomy_events"
    entity_description = "Upcoming Events"

    _attr_icon = "mdi:meteor"

    @property
    def state(self) -> str:
        """Return count of upcoming events."""
        if not self.data.events_fetcher or not self.data.events_fetcher.events:
            return "0"
        return str(len(self.data.events_fetcher.events))

    @property
    def extra_state_attributes(self) -> dict:
        """Return event details."""
        if not self.data.events_fetcher or not self.data.events_fetcher.events:
            return {"events": [], "summary": "No upcoming events"}

        events = []
        now = datetime.now()

        for event in self.data.events_fetcher.events[:5]:  # Next 5 events
            event_time = event.get("datetime", now)
            days_until = (event_time - now).days

            events.append(
                {
                    "name": event.get("name", "Unknown"),
                    "type": event.get("type", "unknown"),
                    "datetime": event_time.isoformat(),
                    "description": event.get("description", ""),
                    "days_until": days_until,
                }
            )

        return {
            "events": events,
            "summary": self.data.events_fetcher.format_events_summary(),
            "last_updated": (
                self.data.events_fetcher.last_updated.isoformat()
                if self.data.events_fetcher.last_updated
                else "Never"
            ),
        }
