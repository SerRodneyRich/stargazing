"""Stargazing sensor platform."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN
from .scoring import StargazingScoringEngine

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up stargazing sensors from config entry."""
    # Get the notify service from config
    notify_service = config_entry.data.get("notify_service", "notify.mandalore")

    # Create scoring engine with default thresholds
    scoring_engine = StargazingScoringEngine(
        min_cloudless=95,
        min_transparency=70,
        min_seeing=65,
    )

    # Create the sensor
    sensor = StargazingQualitySensor(
        hass=hass,
        config_entry=config_entry,
        scoring_engine=scoring_engine,
        notify_service=notify_service,
    )

    async_add_entities([sensor], update_before_add=True)


class StargazingQualitySensor(SensorEntity):
    """Sensor for stargazing quality score."""

    _attr_name = "Stargazing Quality"
    _attr_unique_id = "stargazing_quality_score"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:star"
    _attr_has_entity_name = False

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        scoring_engine: StargazingScoringEngine,
        notify_service: str,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self.config_entry = config_entry
        self.scoring_engine = scoring_engine
        self.notify_service = notify_service
        self._attr_native_value = None

    async def async_added_to_hass(self) -> None:
        """Register state change listener."""
        # Listen for AstroWeather updates
        @callback
        def async_weather_state_listener(event):
            """Handle weather state changes."""
            self.async_schedule_update_ha_state(True)

        self.async_on_remove(
            async_track_state_change_event(
                self.hass,
                ["weather.astroweather_backyard"],
                async_weather_state_listener,
            )
        )

        # Also do initial update
        await self.async_update()

    async def async_update(self) -> None:
        """Update the sensor value."""
        try:
            weather_state = self.hass.states.get("weather.astroweather_backyard")

            if not weather_state or weather_state.state in ("unknown", "unavailable"):
                self._attr_native_value = None
                return

            # Calculate score
            attrs = weather_state.attributes
            score = self.scoring_engine.calculate_score(attrs)

            self._attr_native_value = score

        except Exception as e:
            _LOGGER.error(f"Error updating stargazing sensor: {e}")
            self._attr_native_value = None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        try:
            weather_state = self.hass.states.get("weather.astroweather_backyard")
            if not weather_state or weather_state.state in ("unknown", "unavailable"):
                return {}

            attrs = weather_state.attributes
            score = self._attr_native_value or 0

            return {
                "rating": self.scoring_engine.get_rating(int(score)),
                "emoji": self.scoring_engine.get_rating_emoji(int(score)),
                "cloudless": attrs.get("cloudless_percentage", 0),
                "transparency": attrs.get("transparency_percentage", 0),
                "seeing": attrs.get("seeing_percentage", 0),
                "calm": attrs.get("calm_percentage", 0),
                "moon_phase": attrs.get("moon_phase", 0),
            }
        except Exception as e:
            _LOGGER.error(f"Error getting attributes: {e}")
            return {}
