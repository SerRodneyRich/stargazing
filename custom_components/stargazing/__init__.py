"""The Stargazing integration."""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform

from .const import (
    DOMAIN,
    CONF_NOTIFY_SERVICE,
    CONF_MIN_SCORE,
    CONF_MIN_CLOUDLESS,
    CONF_MIN_TRANSPARENCY,
    CONF_MIN_SEEING,
    DEFAULT_NOTIFY_SERVICE,
    DEFAULT_MIN_SCORE,
    DEFAULT_MIN_CLOUDLESS,
    DEFAULT_MIN_TRANSPARENCY,
    DEFAULT_MIN_SEEING,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

# Support legacy YAML configuration for backward compatibility
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_NOTIFY_SERVICE, default=DEFAULT_NOTIFY_SERVICE): cv.string,
                vol.Optional(CONF_MIN_SCORE, default=DEFAULT_MIN_SCORE): cv.positive_int,
                vol.Optional(CONF_MIN_CLOUDLESS, default=DEFAULT_MIN_CLOUDLESS): cv.positive_int,
                vol.Optional(CONF_MIN_TRANSPARENCY, default=DEFAULT_MIN_TRANSPARENCY): cv.positive_int,
                vol.Optional(CONF_MIN_SEEING, default=DEFAULT_MIN_SEEING): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Stargazing integration from YAML (legacy support)."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]

    # Store config in hass.data so sensor platform can access it
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN]["yaml_config"] = conf

    # Load sensor platform directly via discovery (legacy YAML support)
    hass.async_create_task(
        async_load_platform(
            hass, Platform.SENSOR, DOMAIN, conf, config
        )
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Stargazing from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Store options in data as well for easy access
    if entry.options:
        hass.data[DOMAIN][f"{entry.entry_id}_options"] = entry.options

    # Forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        hass.data[DOMAIN].pop(f"{entry.entry_id}_options", None)

    return unload_ok
