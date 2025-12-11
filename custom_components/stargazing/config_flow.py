"""Config flow for Stargazing integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    DEFAULT_NOTIFY_SERVICE,
    DEFAULT_MIN_SCORE,
    DEFAULT_MIN_CLOUDLESS,
    DEFAULT_MIN_TRANSPARENCY,
    DEFAULT_MIN_SEEING,
    CONF_NOTIFY_SERVICE,
    CONF_MIN_SCORE,
    CONF_MIN_CLOUDLESS,
    CONF_MIN_TRANSPARENCY,
    CONF_MIN_SEEING,
    CONF_ZIP_CODE,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # Validate that AstroWeather integration exists
    weather_state = hass.states.get("weather.astroweather_backyard")
    if not weather_state:
        raise AstroWeatherNotFound

    # Validate notification service if provided
    notify_service = data.get(CONF_NOTIFY_SERVICE)
    if notify_service:
        # Extract just the service name (remove "notify." prefix if present)
        if not notify_service.startswith("notify."):
            notify_service = f"notify.{notify_service}"

        # Check if service exists
        if not hass.services.has_service("notify", notify_service.split(".")[-1]):
            _LOGGER.warning(
                "Notification service '%s' not found - continuing anyway as it may be added later",
                notify_service
            )

    # Return info that will be stored in the config entry
    return {"title": "Stargazing Conditions"}


class AstroWeatherNotFound(Exception):
    """Error to indicate AstroWeather integration is not configured."""


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Stargazing."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except AstroWeatherNotFound:
                errors["base"] = "astroweather_not_found"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create a unique ID to prevent multiple instances
                await self.async_set_unique_id("stargazing_conditions")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_NOTIFY_SERVICE,
                    default=DEFAULT_NOTIFY_SERVICE
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    ),
                ),
                vol.Optional(
                    CONF_MIN_SCORE,
                    default=DEFAULT_MIN_SCORE
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=100,
                        step=1,
                        mode=selector.NumberSelectorMode.SLIDER,
                    ),
                ),
                vol.Optional(
                    CONF_MIN_CLOUDLESS,
                    default=DEFAULT_MIN_CLOUDLESS
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=100,
                        step=1,
                        mode=selector.NumberSelectorMode.SLIDER,
                    ),
                ),
                vol.Optional(
                    CONF_MIN_TRANSPARENCY,
                    default=DEFAULT_MIN_TRANSPARENCY
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=100,
                        step=1,
                        mode=selector.NumberSelectorMode.SLIDER,
                    ),
                ),
                vol.Optional(
                    CONF_MIN_SEEING,
                    default=DEFAULT_MIN_SEEING
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=100,
                        step=1,
                        mode=selector.NumberSelectorMode.SLIDER,
                    ),
                ),
                vol.Optional(
                    CONF_ZIP_CODE,
                    default=""
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                    ),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "notify_service_help": "Enter the name of your notification service (e.g., 'notify.mobile_app_iphone')",
                "min_score_help": "Minimum quality score (0-100) to trigger notifications",
                "cloudless_help": "Minimum cloudless percentage required (recommend 90+)",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Stargazing integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current values from config_entry
        current_data = self.config_entry.data
        current_options = self.config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_NOTIFY_SERVICE,
                        default=current_options.get(
                            CONF_NOTIFY_SERVICE,
                            current_data.get(CONF_NOTIFY_SERVICE, DEFAULT_NOTIFY_SERVICE)
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Optional(
                        CONF_MIN_SCORE,
                        default=current_options.get(
                            CONF_MIN_SCORE,
                            current_data.get(CONF_MIN_SCORE, DEFAULT_MIN_SCORE)
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=100,
                            step=1,
                            mode=selector.NumberSelectorMode.SLIDER,
                        ),
                    ),
                    vol.Optional(
                        CONF_MIN_CLOUDLESS,
                        default=current_options.get(
                            CONF_MIN_CLOUDLESS,
                            current_data.get(CONF_MIN_CLOUDLESS, DEFAULT_MIN_CLOUDLESS)
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=100,
                            step=1,
                            mode=selector.NumberSelectorMode.SLIDER,
                        ),
                    ),
                    vol.Optional(
                        CONF_MIN_TRANSPARENCY,
                        default=current_options.get(
                            CONF_MIN_TRANSPARENCY,
                            current_data.get(CONF_MIN_TRANSPARENCY, DEFAULT_MIN_TRANSPARENCY)
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=100,
                            step=1,
                            mode=selector.NumberSelectorMode.SLIDER,
                        ),
                    ),
                    vol.Optional(
                        CONF_MIN_SEEING,
                        default=current_options.get(
                            CONF_MIN_SEEING,
                            current_data.get(CONF_MIN_SEEING, DEFAULT_MIN_SEEING)
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=100,
                            step=1,
                            mode=selector.NumberSelectorMode.SLIDER,
                        ),
                    ),
                    vol.Optional(
                        CONF_ZIP_CODE,
                        default=current_options.get(
                            CONF_ZIP_CODE,
                            current_data.get(CONF_ZIP_CODE, "")
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                }
            ),
        )
