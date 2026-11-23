"""Eltako ZGW16-IP integration (inoffiziell, nicht von Eltako)."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import EltakoApi
from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from .coordinator import EltakoCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


def gateway_identifier(entry: ConfigEntry) -> tuple[str, str]:
    return (DOMAIN, f"{entry.entry_id}_gateway")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eltako ZGW16-IP gateway (alle Zaehler als Geraete)."""
    hass.data.setdefault(DOMAIN, {})

    api = EltakoApi(
        host=entry.data[CONF_HOST],
        password=entry.data[CONF_PASSWORD],
        session=async_get_clientsession(hass),
    )

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator = EltakoCoordinator(hass, entry, api, scan_interval)
    # Bei falschem Passwort loest das den Reauth-Flow aus.
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Gateway als eigenes Geraet registrieren (Zaehler haengen per via_device_id daran)
    dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={gateway_identifier(entry)},
        manufacturer="Eltako",
        name="Eltako ZGW16-IP",
        model="ZGW16-IP",
        configuration_url=f"http://{entry.data[CONF_HOST]}",
    )

    entry.async_on_unload(entry.add_update_listener(async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Optionen/Daten geaendert: Intervall live anpassen (ohne Neustart)."""
    coordinator: EltakoCoordinator | None = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if coordinator is None:
        return  # Eintrag wird gerade neu geladen oder ist nicht gestartet

    new_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    if coordinator.update_interval.total_seconds() != new_interval:
        hass.bus.async_fire(
            "eltako_zgw16_activity",
            {
                "message": f"Scan-Intervall auf {new_interval} Sekunden geändert",
                "entry_id": entry.entry_id,
            },
        )
        coordinator.update_scan_interval(new_interval)
        await coordinator.async_request_refresh()
