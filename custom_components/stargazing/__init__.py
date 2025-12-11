"""The Stargazing integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.reload import async_setup_reload_service

DOMAIN = "stargazing"
PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Stargazing integration."""
    # Enable reload without restart
    await async_setup_reload_service(hass, DOMAIN, PLATFORMS)

    return True
