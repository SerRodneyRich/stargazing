"""The Stargazing integration - YAML configuration only."""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceResponse, SupportsResponse
from homeassistant.exceptions import ConfigEntryNotFound
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform

_LOGGER = logging.getLogger(__name__)

DOMAIN = "stargazing"
PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional("notify_service", default="notify.mandalore"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Stargazing integration from YAML."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]

    # Store config in hass.data so sensor platform can access it
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["config"] = conf

    # Load sensor platform directly via discovery
    hass.async_create_task(
        async_load_platform(
            hass, Platform.SENSOR, DOMAIN, conf, config
        )
    )

    return True
