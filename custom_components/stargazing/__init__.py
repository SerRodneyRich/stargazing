"""Home Assistant integration for stargazing condition monitoring."""

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
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
)
from .notifications import StargazingNotificationService
from .scoring import StargazingScoringEngine
from .astronomy_events import AstronomyEventsFetcher

_LOGGER = logging.getLogger(__name__)

# Configuration schema
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(
                    CONF_NOTIFY_SERVICE, default=DEFAULT_NOTIFY_SERVICE
                ): cv.string,
                vol.Optional(CONF_MIN_SCORE, default=DEFAULT_MIN_SCORE): cv.positive_int,
                vol.Optional(
                    CONF_MIN_CLOUDLESS, default=DEFAULT_MIN_CLOUDLESS
                ): vol.Range(min=0, max=100),
                vol.Optional(
                    CONF_MIN_TRANSPARENCY, default=DEFAULT_MIN_TRANSPARENCY
                ): vol.Range(min=0, max=100),
                vol.Optional(
                    CONF_MIN_SEEING, default=DEFAULT_MIN_SEEING
                ): vol.Range(min=0, max=100),
                vol.Optional(CONF_ZIP_CODE, default="88431"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


class StargazingData:
    """Shared data for stargazing integration."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize stargazing data."""
        self.hass = hass
        self.config = config

        self.scoring_engine = StargazingScoringEngine(
            min_cloudless=config.get(CONF_MIN_CLOUDLESS, DEFAULT_MIN_CLOUDLESS),
            min_transparency=config.get(CONF_MIN_TRANSPARENCY, DEFAULT_MIN_TRANSPARENCY),
            min_seeing=config.get(CONF_MIN_SEEING, DEFAULT_MIN_SEEING),
        )

        self.notification_service = StargazingNotificationService(
            hass, config.get(CONF_NOTIFY_SERVICE, DEFAULT_NOTIFY_SERVICE)
        )

        self.events_fetcher = None
        self.last_score = None

    async def initialize_events_fetcher(self):
        """Initialize astronomy events fetcher with location."""
        try:
            weather_state = self.hass.states.get("weather.astroweather_backyard")
            if weather_state:
                attrs = weather_state.attributes
                lat = float(attrs.get("latitude", 35.0071952714019))
                lon = float(attrs.get("longitude", -104.155240058899))
                self.events_fetcher = AstronomyEventsFetcher(
                    lat, lon, self.config.get(CONF_ZIP_CODE, "88431")
                )
                await self.events_fetcher.fetch_events()
                _LOGGER.debug(f"Events fetcher initialized at {lat}, {lon}")
        except Exception as e:
            _LOGGER.error(f"Error initializing events fetcher: {e}")

    async def update_stargazing_data(self) -> dict:
        """Update stargazing quality score."""
        try:
            weather_state = self.hass.states.get("weather.astroweather_backyard")
            if not weather_state:
                return {"score": 0, "rating": "Unknown"}

            score = self.scoring_engine.calculate_score(weather_state.attributes)
            rating = self.scoring_engine.get_rating(score)

            self.last_score = score
            return {"score": score, "rating": rating}

        except Exception as e:
            _LOGGER.error(f"Error updating stargazing data: {e}")
            return {"score": 0, "rating": "Error"}


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Stargazing integration."""
    try:
        _LOGGER.info("Setting up Stargazing integration")

        stargazing_config = config.get(DOMAIN, {})
        data = StargazingData(hass, stargazing_config)
        hass.data[DOMAIN] = data

        await data.initialize_events_fetcher()
        await _register_services(hass, data)

        _LOGGER.info("Stargazing integration setup complete")
        return True

    except Exception as e:
        _LOGGER.error(f"Error setting up Stargazing integration: {e}")
        return False


async def _register_services(hass: HomeAssistant, data: StargazingData):
    """Register services."""

    async def handle_test_notification(call):
        """Handle test notification."""
        await data.notification_service.send_test_notification()

    async def handle_check_now(call):
        """Check conditions now."""
        await data.update_stargazing_data()

    async def handle_refresh_events(call):
        """Refresh events."""
        if data.events_fetcher:
            await data.events_fetcher.fetch_events()

    hass.services.async_register(DOMAIN, SERVICE_TEST_NOTIFY, handle_test_notification)
    hass.services.async_register(DOMAIN, SERVICE_CHECK_NOW, handle_check_now)
    hass.services.async_register(DOMAIN, SERVICE_REFRESH_EVENTS, handle_refresh_events)
