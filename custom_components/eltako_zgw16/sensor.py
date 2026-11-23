"""Eltako ZGW16-IP sensors"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import gateway_identifier
from .const import DOMAIN, CONF_DEVICE_ID
from .coordinator import EltakoCoordinator
from .mapping import classify_sensor, normalize_unit

_LOGGER = logging.getLogger(__name__)


def _device_identifier(entry: ConfigEntry, address: int) -> tuple[str, str]:
    """Der urspruenglich konfigurierte Zaehler behaelt seinen alten Identifier."""
    legacy_id = entry.data.get(CONF_DEVICE_ID)
    if legacy_id is not None and int(legacy_id) == int(address):
        return (DOMAIN, entry.entry_id)
    return (DOMAIN, f"{entry.entry_id}_{address}")


def _device_name(device: dict[str, Any], address: int) -> str:
    device_type = device.get("deviceType", "Eltako Device")
    friendly_id = (device.get("friendlyId") or "").strip()
    return f"{friendly_id or device_type} (Bus {address})"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Sensoren fuer alle Zaehler anlegen; neue Zaehler werden automatisch ergaenzt."""
    coordinator: EltakoCoordinator = hass.data[DOMAIN][entry.entry_id]
    known: set[int] = set()

    async def _async_add_new_devices() -> None:
        new_addrs = [a for a in (coordinator.data or {}) if a not in known]
        known.update(new_addrs)  # sofort markieren, vor dem ersten await

        dev_reg = dr.async_get(hass)
        try:
            gateway_id = dr.async_get_device_id_by_identifier(
                hass, gateway_identifier(entry), config_entry_id=entry.entry_id
            )
        except Exception:  # noqa: BLE001
            gateway_id = None

        entities: list[EltakoFunctionSensor] = []
        for addr in new_addrs:
            device = coordinator.data[addr].get("device", {})
            dev_reg.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={_device_identifier(entry, addr)},
                name=_device_name(device, addr),
                manufacturer=device.get("manufacturer", "Eltako"),
                model=device.get("deviceType", "Eltako Device"),
                via_device_id=gateway_id,
            )
            type_id = device.get("deviceTypeId")
            try:
                names = (
                    await coordinator.api.async_get_register_names(type_id)
                    if type_id
                    else {}
                )
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning("Eltako: Register-Namen nicht ladbar: %s", err)
                names = {}

            for func in device.get("functions", []):
                key = func.get("key")
                if not key:
                    continue
                entities.append(
                    EltakoFunctionSensor(
                        coordinator=coordinator,
                        entry=entry,
                        address=addr,
                        function_key=key,
                        friendly_name=names.get(key.strip(), key),
                        unit=func.get("unit"),
                    )
                )

        if entities:
            async_add_entities(entities)
            _LOGGER.info("Eltako: %d sensors added", len(entities))

    @callback
    def _handle_coordinator_update() -> None:
        if any(a not in known for a in (coordinator.data or {})):
            hass.async_create_task(_async_add_new_devices())

    entry.async_on_unload(coordinator.async_add_listener(_handle_coordinator_update))
    await _async_add_new_devices()


class EltakoFunctionSensor(CoordinatorEntity[EltakoCoordinator], SensorEntity):
    """Eine Funktion (Register) eines Eltako-Zaehlers."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EltakoCoordinator,
        entry: ConfigEntry,
        address: int,
        function_key: str,
        friendly_name: str,
        unit: str | None,
    ) -> None:
        super().__init__(coordinator)
        self._address = address
        self._function_key = function_key.strip()

        # Bestehende Installationen (mit device_id im Entry) behalten das
        # Praefix "Eltako", damit sich Anzeigenamen nicht aendern. Neue
        # Installationen bekommen den sauberen Namen ohne Praefix.
        has_legacy_entry = CONF_DEVICE_ID in entry.data
        self._attr_name = f"Eltako {friendly_name}" if has_legacy_entry else friendly_name

        self._attr_native_unit_of_measurement = normalize_unit(unit)
        self._attr_device_class, self._attr_state_class = classify_sensor(
            unit, friendly_name
        )

        identifier = _device_identifier(entry, address)
        if identifier == (DOMAIN, entry.entry_id):
            # Legacy-Zaehler: alte unique_id beibehalten (Historie bleibt)
            self._attr_unique_id = f"{entry.entry_id}_{self._function_key}"
        else:
            self._attr_unique_id = f"{entry.entry_id}_{address}_{self._function_key}"

        device = coordinator.data[address].get("device", {})
        # via_device_id wird beim Registrieren des Geraets gesetzt (siehe oben)
        self._attr_device_info = DeviceInfo(
            identifiers={identifier},
            name=_device_name(device, address),
            manufacturer=device.get("manufacturer", "Eltako"),
            model=device.get("deviceType", "Eltako Device"),
        )

    @property
    def available(self) -> bool:
        return super().available and self._address in (self.coordinator.data or {})

    @property
    def native_value(self) -> Any | None:
        data = (self.coordinator.data or {}).get(self._address)
        if not data:
            return None
        for func in data.get("device", {}).get("functions", []):
            if func.get("key", "").strip() == self._function_key:
                return func.get("value")
        return None
