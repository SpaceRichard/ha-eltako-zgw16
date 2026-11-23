"""Coordinator for the Eltako ZGW16-IP integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EltakoApi, EltakoAuthError

_LOGGER = logging.getLogger(__name__)


class EltakoCoordinator(DataUpdateCoordinator[dict[int, dict[str, Any]]]):
    """Coordinator: liefert {busAddress: Geraetedaten} fuer alle Zaehler."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        api: EltakoApi,
        scan_interval: int,
    ) -> None:
        self.api = api
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            config_entry=entry,
            name="Eltako ZGW16-IP",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[int, dict[str, Any]]:
        try:
            await self.api.async_ensure_login()
            devices = await self.api.async_get_devices()
        except EltakoAuthError as err:
            # Startet den Reauth-Flow (neues Passwort abfragen)
            raise ConfigEntryAuthFailed(str(err)) from err
        except Exception as err:
            raise UpdateFailed(f"Error fetching Eltako device list: {err}") from err

        addresses = [d["busAddress"] for d in devices if "busAddress" in d]

        results = await asyncio.gather(
            *(self.api.async_get_device_data(a) for a in addresses),
            return_exceptions=True,
        )

        data: dict[int, dict[str, Any]] = {}
        for addr, res in zip(addresses, results):
            if isinstance(res, EltakoAuthError):
                raise ConfigEntryAuthFailed(str(res)) from res
            if isinstance(res, Exception):
                _LOGGER.warning("Eltako: Zaehler (Bus %s) nicht abrufbar: %s", addr, res)
                continue
            data[addr] = res

        if addresses and not data:
            raise UpdateFailed("Kein Zaehler am Gateway abrufbar")
        return data

    def update_scan_interval(self, seconds: int) -> None:
        """Update polling interval live (no HA restart)."""
        self.update_interval = timedelta(seconds=seconds)
        _LOGGER.info("Eltako scan interval updated to %s seconds", seconds)
