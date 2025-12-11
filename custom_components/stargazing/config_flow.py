"""Config flow for Stargazing integration."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

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
)

_LOGGER = __import__("logging").getLogger(__name__)


class StargazingConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Stargazing."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="Stargazing Conditions", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NOTIFY_SERVICE, default=DEFAULT_NOTIFY_SERVICE
                    ): str,
                    vol.Optional(
                        CONF_MIN_SCORE, default=DEFAULT_MIN_SCORE
                    ): int,
                    vol.Optional(
                        CONF_MIN_CLOUDLESS, default=DEFAULT_MIN_CLOUDLESS
                    ): vol.Range(min=0, max=100),
                    vol.Optional(
                        CONF_MIN_TRANSPARENCY, default=DEFAULT_MIN_TRANSPARENCY
                    ): vol.Range(min=0, max=100),
                    vol.Optional(
                        CONF_MIN_SEEING, default=DEFAULT_MIN_SEEING
                    ): vol.Range(min=0, max=100),
                    vol.Optional(CONF_ZIP_CODE, default="88431"): str,
                }
            ),
        )
