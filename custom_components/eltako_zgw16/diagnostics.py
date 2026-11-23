"""Diagnostics for Eltako ZGW16-IP (Zugangsdaten geschwaerzt)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_HOST, CONF_PASSWORD

TO_REDACT = {CONF_HOST, CONF_PASSWORD, "friendlyId"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    return {
        "entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "entry_options": dict(entry.options),
        "update_interval_s": coordinator.update_interval.total_seconds(),
        "last_update_success": coordinator.last_update_success,
        "devices": {
            str(addr): async_redact_data(data, TO_REDACT)
            for addr, data in (coordinator.data or {}).items()
        },
    }
