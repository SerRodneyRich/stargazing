"""Stargazing sensor platform."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    CONF_MIN_CLOUDLESS,
    CONF_MIN_TRANSPARENCY,
    CONF_MIN_SEEING,
    CONF_ZIP_CODE,
    DEFAULT_MIN_CLOUDLESS,
    DEFAULT_MIN_TRANSPARENCY,
    DEFAULT_MIN_SEEING,
)
from .scoring import StargazingScoringEngine
from .astronomy_events import AstronomyEventsFetcher

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up stargazing sensors from a config entry."""
    # Get configuration from entry
    config = entry.data
    options = entry.options

    # Merge config and options (options take precedence)
    min_cloudless = options.get(CONF_MIN_CLOUDLESS, config.get(CONF_MIN_CLOUDLESS, DEFAULT_MIN_CLOUDLESS))
    min_transparency = options.get(CONF_MIN_TRANSPARENCY, config.get(CONF_MIN_TRANSPARENCY, DEFAULT_MIN_TRANSPARENCY))
    min_seeing = options.get(CONF_MIN_SEEING, config.get(CONF_MIN_SEEING, DEFAULT_MIN_SEEING))
    zip_code = options.get(CONF_ZIP_CODE, config.get(CONF_ZIP_CODE, "88431"))

    # Create scoring engine with configured standards
    scoring_engine = StargazingScoringEngine(
        min_cloudless=min_cloudless,
        min_transparency=min_transparency,
        min_seeing=min_seeing,
    )

    # Initialize events fetcher
    events_fetcher = None
    try:
        weather_state = hass.states.get("weather.astroweather_backyard")
        if weather_state:
            attrs = weather_state.attributes
            lat = float(attrs.get("latitude", 35.0071952714019))
            lon = float(attrs.get("longitude", -104.155240058899))
            events_fetcher = AstronomyEventsFetcher(lat, lon, zip_code)
            await events_fetcher.fetch_events()
    except Exception as e:
        _LOGGER.error(f"Error initializing events fetcher: {e}")

    # Create all sensor entities
    entities = [
        StargazingQualitySensor(hass, entry, scoring_engine),
        StargazingRatingSensor(hass, entry, scoring_engine),
        OptimalViewingStartSensor(hass, entry),
        OptimalViewingEndSensor(hass, entry),
        UpcomingEventsSensor(hass, entry, events_fetcher),
        NextEvent1Sensor(hass, entry, events_fetcher),
        NextEvent2Sensor(hass, entry, events_fetcher),
        NextEvent3Sensor(hass, entry, events_fetcher),
    ]

    async_add_entities(entities, update_before_add=False)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict | None = None,
) -> None:
    """Set up stargazing sensors from YAML configuration (legacy support)."""
    # Get config from discovery_info (passed from __init__.py)
    if discovery_info:
        notify_service = discovery_info.get("notify_service", "notify.mandalore")
    else:
        # Fallback to hass.data if available
        notify_service = hass.data.get(DOMAIN, {}).get(
            "notify_service", "notify.mandalore"
        )

    # Create scoring engine with high standards
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

    # Create all sensor entities (legacy - no config entry)
    entities = [
        StargazingQualitySensor(hass, None, scoring_engine),
        StargazingRatingSensor(hass, None, scoring_engine),
        OptimalViewingStartSensor(hass, None),
        OptimalViewingEndSensor(hass, None),
        UpcomingEventsSensor(hass, None, events_fetcher),
        NextEvent1Sensor(hass, None, events_fetcher),
        NextEvent2Sensor(hass, None, events_fetcher),
        NextEvent3Sensor(hass, None, events_fetcher),
    ]

    async_add_entities(entities, update_before_add=True)


class StargazingBaseSensor(SensorEntity):
    """Base sensor for stargazing."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry | None) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry = entry
        self._attr_native_value = None

        # Set up device info if we have a config entry
        if entry:
            self._attr_device_info = DeviceInfo(
                entry_type=DeviceEntryType.SERVICE,
                identifiers={(DOMAIN, entry.entry_id)},
                name="Stargazing Conditions",
                manufacturer="Stargazing Integration",
                model="Astronomy Monitor",
                sw_version="1.0.0",
            )

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

    _attr_name = "Quality"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:star"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry | None, scoring_engine: StargazingScoringEngine) -> None:
        """Initialize sensor with scoring engine."""
        super().__init__(hass, entry)
        self.scoring_engine = scoring_engine
        # Set unique_id based on entry or use legacy ID
        if entry:
            self._attr_unique_id = f"{entry.entry_id}_quality_score"
        else:
            self._attr_unique_id = "stargazing_quality_score"

    async def async_update(self) -> None:
        """Update the sensor value."""
        try:
            weather_state = self.hass.states.get("weather.astroweather_backyard")
            if not weather_state or weather_state.state in ("unknown", "unavailable"):
                self._attr_native_value = None
                return

            attrs = weather_state.attributes
            score = self.scoring_engine.calculate_score(attrs)
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

            return {
                "rating": self.scoring_engine.get_rating(int(score)),
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

    _attr_name = "Rating"
    _attr_icon = "mdi:sparkles"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry | None, scoring_engine: StargazingScoringEngine) -> None:
        """Initialize sensor with scoring engine."""
        super().__init__(hass, entry)
        self.scoring_engine = scoring_engine
        # Set unique_id based on entry or use legacy ID
        if entry:
            self._attr_unique_id = f"{entry.entry_id}_rating"
        else:
            self._attr_unique_id = "stargazing_rating"

    async def async_update(self) -> None:
        """Update the sensor value."""
        try:
            weather_state = self.hass.states.get("weather.astroweather_backyard")
            if not weather_state or weather_state.state in ("unknown", "unavailable"):
                self._attr_native_value = "Unknown"
                return

            attrs = weather_state.attributes
            score = self.scoring_engine.calculate_score(attrs)
            self._attr_native_value = self.scoring_engine.get_rating(score)

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
            score = self.scoring_engine.calculate_score(attrs)

            return {
                "emoji": self.scoring_engine.get_rating_emoji(score),
                "score": score,
            }
        except Exception as e:
            _LOGGER.error(f"Error getting rating attributes: {e}")
            return {}


class OptimalViewingStartSensor(StargazingBaseSensor):
    """Sensor for optimal viewing start time."""

    _attr_name = "Optimal Start"
    _attr_icon = "mdi:sunset-down"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry | None) -> None:
        """Initialize the sensor."""
        super().__init__(hass, entry)
        # Set unique_id based on entry or use legacy ID
        if entry:
            self._attr_unique_id = f"{entry.entry_id}_optimal_start"
        else:
            self._attr_unique_id = "stargazing_optimal_start"

    async def async_update(self) -> None:
        """Update the sensor value."""
        try:
            sun_dusk = self.hass.states.get("sensor.sun_next_dusk")
            if not sun_dusk or sun_dusk.state in ("unknown", "unavailable"):
                self._attr_native_value = "Unknown"
                return

            dusk_time = datetime.fromisoformat(sun_dusk.state.replace("Z", "+00:00"))
            local_dusk = dusk_time.astimezone()
            self._attr_native_value = local_dusk.strftime("%I:%M %p")

        except Exception as e:
            _LOGGER.error(f"Error updating optimal start: {e}")
            self._attr_native_value = "Error"


class OptimalViewingEndSensor(StargazingBaseSensor):
    """Sensor for optimal viewing end time."""

    _attr_name = "Optimal End"
    _attr_icon = "mdi:moon-waning-crescent"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry | None) -> None:
        """Initialize the sensor."""
        super().__init__(hass, entry)
        # Set unique_id based on entry or use legacy ID
        if entry:
            self._attr_unique_id = f"{entry.entry_id}_optimal_end"
        else:
            self._attr_unique_id = "stargazing_optimal_end"

    async def async_update(self) -> None:
        """Update the sensor value."""
        try:
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

    _attr_name = "Upcoming Events"
    _attr_icon = "mdi:meteor"
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry | None, events_fetcher) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry = entry
        self.events_fetcher = events_fetcher
        self._attr_native_value = 0

        # Set unique_id based on entry or use legacy ID
        if entry:
            self._attr_unique_id = f"{entry.entry_id}_upcoming_events"
            self._attr_device_info = DeviceInfo(
                entry_type=DeviceEntryType.SERVICE,
                identifiers={(DOMAIN, entry.entry_id)},
                name="Stargazing Conditions",
                manufacturer="Stargazing Integration",
                model="Astronomy Monitor",
                sw_version="1.0.0",
            )
        else:
            self._attr_unique_id = "stargazing_upcoming_events"

    async def async_added_to_hass(self) -> None:
        """Register state change listener and do initial update."""
        # Do initial update
        await self.async_update()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if not self.events_fetcher or not self.events_fetcher.events:
            return {"events": [], "summary": "No upcoming events"}

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


class BaseEventSensor(SensorEntity):
    """Base class for individual event sensors."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_icon = "mdi:calendar-star"

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry | None,
        events_fetcher,
        event_index: int,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry = entry
        self.events_fetcher = events_fetcher
        self.event_index = event_index
        self._attr_native_value = None

        # Set up device info if we have a config entry
        if entry:
            self._attr_device_info = DeviceInfo(
                entry_type=DeviceEntryType.SERVICE,
                identifiers={(DOMAIN, entry.entry_id)},
                name="Stargazing Conditions",
                manufacturer="Stargazing Integration",
                model="Astronomy Monitor",
                sw_version="1.0.0",
            )

    async def async_added_to_hass(self) -> None:
        """Do initial update when added."""
        await self.async_update()

    async def async_update(self) -> None:
        """Update the sensor value."""
        if not self.events_fetcher or not self.events_fetcher.events:
            self._attr_native_value = "No events"
            return

        now = datetime.now()
        upcoming = [
            e for e in self.events_fetcher.events if e.get("datetime", now) >= now
        ]

        if len(upcoming) > self.event_index:
            event = upcoming[self.event_index]
            event_time = event.get("datetime", now)
            days_until = (event_time - now).days

            if days_until == 0:
                when = "Tonight"
            elif days_until == 1:
                when = "Tomorrow"
            else:
                when = f"In {days_until} days"

            # Full summary as state
            time_str = event_time.strftime("%I:%M %p")
            self._attr_native_value = f"{event.get('name', 'Unknown')} - {when} at {time_str}"
            self._event_data = event
        else:
            self._attr_native_value = "No event scheduled"
            self._event_data = None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if not hasattr(self, "_event_data") or not self._event_data:
            return {}

        now = datetime.now()
        event_time = self._event_data.get("datetime", now)
        days_until = (event_time - now).days

        return {
            "type": self._event_data.get("type", "unknown"),
            "description": self._event_data.get("description", ""),
            "datetime": event_time.isoformat(),
            "days_until": days_until,
            "when": (
                "Tonight"
                if days_until == 0
                else "Tomorrow" if days_until == 1 else f"In {days_until} days"
            ),
            "date": event_time.strftime("%b %d, %Y"),
            "time": event_time.strftime("%I:%M %p"),
        }


class NextEvent1Sensor(BaseEventSensor):
    """Sensor for next astronomy event."""

    _attr_name = "Next Event"

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry | None, events_fetcher
    ) -> None:
        """Initialize the sensor."""
        super().__init__(hass, entry, events_fetcher, 0)
        if entry:
            self._attr_unique_id = f"{entry.entry_id}_next_event_1"
        else:
            self._attr_unique_id = "stargazing_next_event_1"


class NextEvent2Sensor(BaseEventSensor):
    """Sensor for second upcoming astronomy event."""

    _attr_name = "Next Event 2"

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry | None, events_fetcher
    ) -> None:
        """Initialize the sensor."""
        super().__init__(hass, entry, events_fetcher, 1)
        if entry:
            self._attr_unique_id = f"{entry.entry_id}_next_event_2"
        else:
            self._attr_unique_id = "stargazing_next_event_2"


class NextEvent3Sensor(BaseEventSensor):
    """Sensor for third upcoming astronomy event."""

    _attr_name = "Next Event 3"

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry | None, events_fetcher
    ) -> None:
        """Initialize the sensor."""
        super().__init__(hass, entry, events_fetcher, 2)
        if entry:
            self._attr_unique_id = f"{entry.entry_id}_next_event_3"
        else:
            self._attr_unique_id = "stargazing_next_event_3"
