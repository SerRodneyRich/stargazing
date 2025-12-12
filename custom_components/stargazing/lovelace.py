"""Lovelace resources for Stargazing integration."""
from homeassistant.components.lovelace import _register_panel
from homeassistant.core import HomeAssistant

CARD_URL = "/hacsfiles/stargazing/stargazing-card.js"


async def async_register_card(hass: HomeAssistant) -> None:
    """Register the Stargazing card."""
    # Add the card to the Lovelace resources
    try:
        await hass.components.lovelace.async_register_resource(
            CARD_URL,
            "module",
        )
    except Exception:
        # Resource already registered or method doesn't exist
        pass
