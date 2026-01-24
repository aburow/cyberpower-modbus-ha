"""Config flow for the APC UPS Modbus integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DEFAULT_UNIT, CONF_UNIT


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        vol.Optional(CONF_UNIT, default=DEFAULT_UNIT): int,
    }
)


class APCModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle APC UPS Modbus config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial config flow step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        return self.async_create_entry(
            title=user_input[CONF_HOST],
            data={**user_input},
        )
