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
from .astronomy_events import AstronomyEventsFetcher

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up stargazing sensors from config entry."""
    # Create scoring engine with default thresholds
    scoring_engine = StargazingScoringEngine(
        min_cloudless=95,
        min_transparency=70,
        min_seeing=65,
    )

    # Initialize events fetcher
    events_fetcher = None
    try:
        weather_state = hass.states.get("weather.astroweather_backyard")
        if weather_state:
            attrs = weather_state.attributes
            lat = float(attrs.get("latitude", 35.0071952714019))
            lon = float(attrs.get("longitude", -104.155240058899))
            events_fetcher = AstronomyEventsFetcher(lat, lon, "88431")
            await events_fetcher.fetch_events()
    except Exception as e:
        _LOGGER.error(f"Error initializing events fetcher: {e}")

    # Create all sensor entities
    entities = [
        StargazingQualitySensor(hass, config_entry, scoring_engine),
        StargazingRatingSensor(hass, config_entry, scoring_engine),
        OptimalViewingStartSensor(hass, config_entry),
        OptimalViewingEndSensor(hass, config_entry),
        UpcomingEventsSensor(hass, config_entry, events_fetcher),
    ]

    async_add_entities(entities, update_before_add=True)


class StargazingBaseSensor(SensorEntity):
    """Base sensor for stargazing."""

    _attr_has_entity_name = False

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self.config_entry = config_entry
        self._attr_native_value = None

    async def async_added_to_hass(self) -> None:
        """Register state change listener."""
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

        # Do initial update
        await self.async_update()


class StargazingQualitySensor(StargazingBaseSensor):
    """Sensor for stargazing quality score."""

    _attr_name = "Stargazing Quality"
    _attr_unique_id = "stargazing_quality_score"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:star"

    async def async_update(self) -> None:
        """Update the sensor value."""
        try:
            weather_state = self.hass.states.get("weather.astroweather_backyard")
            if not weather_state or weather_state.state in ("unknown", "unavailable"):
                self._attr_native_value = None
                return

            attrs = weather_state.attributes
            scoring_engine = StargazingScoringEngine(95, 70, 65)
            score = scoring_engine.calculate_score(attrs)
            self._attr_native_value = score

        except Exception as e:
            _LOGGER.error(f"Error updating quality score: {e}")
            self._attr_native_value = None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        try:
            weather_state = self.hass.states.get("weather.astroweather_backyard")
            if not weather_state:
                return {}

            attrs = weather_state.attributes
            score = self._attr_native_value or 0
            scoring_engine = StargazingScoringEngine(95, 70, 65)

            return {
                "rating": scoring_engine.get_rating(int(score)),
                "cloudless": attrs.get("cloudless_percentage", 0),
                "transparency": attrs.get("transparency_percentage", 0),
                "seeing": attrs.get("seeing_percentage", 0),
                "calm": attrs.get("calm_percentage", 0),
                "moon_phase": attrs.get("moon_phase", 0),
            }
        except Exception as e:
            _LOGGER.error(f"Error getting quality attributes: {e}")
            return {}


class StargazingRatingSensor(StargazingBaseSensor):
    """Sensor for stargazing rating (EXCEPTIONAL/AMAZING/Good/Poor)."""

    _attr_name = "Stargazing Rating"
    _attr_unique_id = "stargazing_rating"
    _attr_icon = "mdi:sparkles"

    async def async_update(self) -> None:
        """Update the sensor value."""
        try:
            weather_state = self.hass.states.get("weather.astroweather_backyard")
            if not weather_state or weather_state.state in ("unknown", "unavailable"):
                self._attr_native_value = "Unknown"
                return

            attrs = weather_state.attributes
            scoring_engine = StargazingScoringEngine(95, 70, 65)
            score = scoring_engine.calculate_score(attrs)
            self._attr_native_value = scoring_engine.get_rating(score)

        except Exception as e:
            _LOGGER.error(f"Error updating rating: {e}")
            self._attr_native_value = "Error"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        try:
            weather_state = self.hass.states.get("weather.astroweather_backyard")
            if not weather_state:
                return {}

            attrs = weather_state.attributes
            scoring_engine = StargazingScoringEngine(95, 70, 65)
            score = scoring_engine.calculate_score(attrs)

            return {
                "emoji": scoring_engine.get_rating_emoji(score),
                "score": score,
            }
        except Exception as e:
            _LOGGER.error(f"Error getting rating attributes: {e}")
            return {}


class OptimalViewingStartSensor(StargazingBaseSensor):
    """Sensor for optimal viewing start time."""

    _attr_name = "Stargazing Optimal Start"
    _attr_unique_id = "stargazing_optimal_start"
    _attr_icon = "mdi:sunset-down"

    async def async_update(self) -> None:
        """Update the sensor value."""
        try:
            sun_dusk = self.hass.states.get("sensor.sun_next_dusk")
            if not sun_dusk or sun_dusk.state in ("unknown", "unavailable"):
                self._attr_native_value = "Unknown"
                return

            from datetime import datetime
            dusk_time = datetime.fromisoformat(sun_dusk.state.replace("Z", "+00:00"))
            local_dusk = dusk_time.astimezone()
            self._attr_native_value = local_dusk.strftime("%I:%M %p")

        except Exception as e:
            _LOGGER.error(f"Error updating optimal start: {e}")
            self._attr_native_value = "Error"


class OptimalViewingEndSensor(StargazingBaseSensor):
    """Sensor for optimal viewing end time."""

    _attr_name = "Stargazing Optimal End"
    _attr_unique_id = "stargazing_optimal_end"
    _attr_icon = "mdi:moon-waning-crescent"

    async def async_update(self) -> None:
        """Update the sensor value."""
        try:
            from datetime import datetime, timedelta
            sun_setting = self.hass.states.get("sensor.sun_next_setting")
            if not sun_setting or sun_setting.state in ("unknown", "unavailable"):
                self._attr_native_value = "Unknown"
                return

            sunset_time = datetime.fromisoformat(
                sun_setting.state.replace("Z", "+00:00")
            )
            local_midnight = (
                sunset_time.replace(hour=0, minute=0, second=0) + timedelta(days=1)
            ).astimezone()
            self._attr_native_value = local_midnight.strftime("%I:%M %p")

        except Exception as e:
            _LOGGER.error(f"Error updating optimal end: {e}")
            self._attr_native_value = "Error"


class UpcomingEventsSensor(SensorEntity):
    """Sensor for upcoming astronomy events."""

    _attr_name = "Stargazing Upcoming Events"
    _attr_unique_id = "stargazing_upcoming_events"
    _attr_icon = "mdi:meteor"
    _attr_has_entity_name = False

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        events_fetcher,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self.config_entry = config_entry
        self.events_fetcher = events_fetcher
        self._attr_native_value = 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if not self.events_fetcher or not self.events_fetcher.events:
            return {"events": [], "summary": "No upcoming events"}

        from datetime import datetime

        events = []
        now = datetime.now()

        for event in self.events_fetcher.events[:5]:
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
            "summary": self.events_fetcher.format_events_summary(),
        }

    async def async_update(self) -> None:
        """Update event count."""
        if self.events_fetcher and self.events_fetcher.events:
            self._attr_native_value = len(self.events_fetcher.events)
        else:
            self._attr_native_value = 0
