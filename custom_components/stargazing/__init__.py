"""The Stargazing integration - YAML configuration only."""
from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

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
    hass.data[DOMAIN] = conf

    # Load sensor platform
    await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "import"}, data=conf
    )

    return True
