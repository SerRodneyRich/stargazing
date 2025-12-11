"""Home Assistant integration for stargazing condition monitoring."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .astronomy_events import AstronomyEventsFetcher
from .const import (
    ASTROWEATHER_WEATHER,
    BINARY_DEEP_SKY_VIEW,
    CONF_CHECK_TIMES,
    CONF_MIN_CLOUDLESS,
    CONF_MIN_SCORE,
    CONF_MIN_SEEING,
    CONF_MIN_TRANSPARENCY,
    CONF_NOTIFY_SERVICE,
    CONF_ZIP_CODE,
    DEFAULT_MIN_CLOUDLESS,
    DEFAULT_MIN_SCORE,
    DEFAULT_MIN_SEEING,
    DEFAULT_MIN_TRANSPARENCY,
    DEFAULT_NOTIFY_SERVICE,
    DOMAIN,
    SERVICE_CHECK_NOW,
    SERVICE_REFRESH_EVENTS,
    SERVICE_TEST_NOTIFY,
    SUN_NEXT_DUSK,
    SUN_NEXT_SETTING,
    UPDATE_INTERVAL_EVENTS,
    UPDATE_INTERVAL_SCORE,
)
from .notifications import StargazingNotificationService
from .scoring import StargazingScoringEngine

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

# Configuration schema
STARGAZING_CONFIG_SCHEMA = {
    CONF_NOTIFY_SERVICE: DEFAULT_NOTIFY_SERVICE,
    CONF_MIN_SCORE: DEFAULT_MIN_SCORE,
    CONF_MIN_CLOUDLESS: DEFAULT_MIN_CLOUDLESS,
    CONF_MIN_TRANSPARENCY: DEFAULT_MIN_TRANSPARENCY,
    CONF_MIN_SEEING: DEFAULT_MIN_SEEING,
    CONF_ZIP_CODE: "88431",
    CONF_CHECK_TIMES: ["15:00"],
}


class StargazingData:
    """Shared data for stargazing integration."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize stargazing data.

        Args:
            hass: Home Assistant instance
            config: Configuration dict
        """
        self.hass = hass
        self.config = {**STARGAZING_CONFIG_SCHEMA, **config}

        # Initialize components
        self.scoring_engine = StargazingScoringEngine(
            min_cloudless=self.config[CONF_MIN_CLOUDLESS],
            min_transparency=self.config[CONF_MIN_TRANSPARENCY],
            min_seeing=self.config[CONF_MIN_SEEING],
        )

        self.notification_service = StargazingNotificationService(
            hass, self.config[CONF_NOTIFY_SERVICE]
        )

        self.events_fetcher: Optional[AstronomyEventsFetcher] = None

        # State tracking
        self.last_score: Optional[int] = None
        self.last_notification_type: Optional[str] = None
        self.last_notification_time: Optional[datetime] = None
        self.last_events_fetch: Optional[datetime] = None

    async def initialize_events_fetcher(self):
        """Initialize astronomy events fetcher with location."""
        try:
            weather_state = self.hass.states.get(ASTROWEATHER_WEATHER)
            if weather_state:
                attrs = weather_state.attributes
                lat = float(attrs.get("latitude", 35.0071952714019))
                lon = float(attrs.get("longitude", -104.155240058899))
                self.events_fetcher = AstronomyEventsFetcher(
                    lat, lon, self.config.get(CONF_ZIP_CODE)
                )
                await self.events_fetcher.fetch_events()
                _LOGGER.debug(f"Events fetcher initialized at {lat}, {lon}")
        except Exception as e:
            _LOGGER.error(f"Error initializing events fetcher: {e}")

    async def update_stargazing_data(self) -> dict:
        """Update stargazing quality score and related data.

        Returns:
            Dict with score, rating, and metadata
        """
        try:
            weather_state = self.hass.states.get(ASTROWEATHER_WEATHER)
            if not weather_state:
                _LOGGER.warning("AstroWeather entity not found")
                return {"score": 0, "rating": "Unknown", "error": "AstroWeather unavailable"}

            # Calculate score
            score = self.scoring_engine.calculate_score(weather_state.attributes)
            rating = self.scoring_engine.get_rating(score)
            breakdown = self.scoring_engine.get_score_breakdown(weather_state.attributes)

            # Calculate viewing window
            try:
                sun_setting = self.hass.states.get(SUN_NEXT_SETTING)
                sun_dusk = self.hass.states.get(SUN_NEXT_DUSK)

                if sun_setting and sun_dusk:
                    sunset_time = datetime.fromisoformat(
                        sun_setting.state.replace("Z", "+00:00")
                    )
                    dusk_time = datetime.fromisoformat(
                        sun_dusk.state.replace("Z", "+00:00")
                    )

                    # Convert to local time for display
                    local_sunset = sunset_time.astimezone()
                    local_dusk = dusk_time.astimezone()
                    local_midnight = (
                        sunset_time.replace(hour=0, minute=0, second=0)
                        + timedelta(days=1)
                    ).astimezone()

                    optimal_window = {
                        "start": local_dusk.strftime("%I:%M %p"),
                        "end": local_midnight.strftime("%I:%M %p"),
                        "start_time": local_dusk,
                        "end_time": local_midnight,
                    }
                else:
                    optimal_window = {"start": "N/A", "end": "N/A"}
            except Exception as e:
                _LOGGER.debug(f"Error calculating viewing window: {e}")
                optimal_window = {"start": "N/A", "end": "N/A"}

            data = {
                "score": score,
                "rating": rating,
                "emoji": self.scoring_engine.get_rating_emoji(score),
                "cloudless": breakdown.get("cloudless", {}).get("value", 0),
                "transparency": breakdown.get("transparency", {}).get("value", 0),
                "seeing": breakdown.get("seeing", {}).get("value", 0),
                "calm": breakdown.get("calm", {}).get("value", 0),
                "moon_phase": breakdown.get("moon_phase", {}).get("value", 0),
                "optimal_window": optimal_window,
                "breakdown": breakdown,
            }

            self.last_score = score
            return data

        except Exception as e:
            _LOGGER.error(f"Error updating stargazing data: {e}")
            return {"score": 0, "rating": "Error", "error": str(e)}

    async def check_and_notify(self):
        """Check conditions and send notifications if warranted."""
        try:
            data = await self.update_stargazing_data()
            score = data.get("score", 0)

            # Avoid notification spam: only notify once per score level per hour
            now = datetime.now()
            if self.last_notification_time:
                if (now - self.last_notification_time).total_seconds() < 3600:
                    if self.last_notification_type == self.scoring_engine.get_rating(
                        score
                    ):
                        return  # Already notified recently

            # Send appropriate notification
            if score >= 90:
                await self.notification_service.send_exceptional_alert(
                    score, data.get("breakdown", {}), data.get("optimal_window", {})
                )
                self.last_notification_type = "EXCEPTIONAL"
                self.last_notification_time = now

            elif score >= 80:
                await self.notification_service.send_amazing_conditions_alert(
                    score, data.get("breakdown", {}), data.get("optimal_window", {})
                )
                self.last_notification_type = "AMAZING"
                self.last_notification_time = now

        except Exception as e:
            _LOGGER.error(f"Error in check_and_notify: {e}")


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Stargazing integration."""
    try:
        _LOGGER.info("Setting up Stargazing integration")

        # Get config from configuration.yaml
        stargazing_config = config.get(DOMAIN, {})

        # Create shared data
        data = StargazingData(hass, stargazing_config)
        hass.data[DOMAIN] = data

        # Initialize events fetcher
        await data.initialize_events_fetcher()

        # Register services
        await _async_setup_services(hass, data)

        _LOGGER.info("Stargazing integration setup complete")
        return True

    except Exception as e:
        _LOGGER.error(f"Error setting up Stargazing integration: {e}")
        return False


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Stargazing from a config entry."""
    try:
        # Create shared data from config entry
        data = StargazingData(hass, dict(entry.data))
        hass.data[DOMAIN] = data

        # Initialize events fetcher
        await data.initialize_events_fetcher()

        # Register services
        await _async_setup_services(hass, data)

        # Forward to sensor platform
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        _LOGGER.info("Stargazing config entry setup complete")
        return True

    except Exception as e:
        _LOGGER.error(f"Error setting up Stargazing config entry: {e}")
        return False


async def _async_setup_services(hass: HomeAssistant, data: StargazingData):
    """Register all services."""

    async def handle_test_notification(call):
        """Handle test notification service call."""
        _LOGGER.info("Test notification service called")
        result = await data.notification_service.send_test_notification()
        if result:
            _LOGGER.info("Test notification sent successfully")
        else:
            _LOGGER.warning("Test notification failed")

    async def handle_check_now(call):
        """Handle immediate condition check."""
        _LOGGER.info("Manual condition check requested")
        await data.check_and_notify()

    async def handle_refresh_events(call):
        """Handle events refresh."""
        _LOGGER.info("Astronomy events refresh requested")
        if data.events_fetcher:
            await data.events_fetcher.fetch_events()
            _LOGGER.info("Events refreshed")
        else:
            _LOGGER.warning("Events fetcher not initialized")

    # Register services
    hass.services.async_register(
        DOMAIN, SERVICE_TEST_NOTIFY, handle_test_notification
    )
    hass.services.async_register(DOMAIN, SERVICE_CHECK_NOW, handle_check_now)
    hass.services.async_register(DOMAIN, SERVICE_REFRESH_EVENTS, handle_refresh_events)

    _LOGGER.info("Services registered: test_notification, check_now, refresh_events")
