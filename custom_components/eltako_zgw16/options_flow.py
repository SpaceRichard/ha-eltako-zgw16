"""Options flow for Eltako ZGW16-IP."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL


class EltakoZgw16OptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for Eltako ZGW16-IP."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self._entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self._entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=current_interval
                    ): vol.All(int, vol.Range(min=5, max=300))
                }
            ),
        )
