"""Einheiten- und Klassen-Zuordnung fuer Eltako-Register (ohne HA-Entity-Logik)."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

# Das Gateway liefert teils ausgeschriebene Einheiten ("Volt"), HA erwartet Symbole.
_UNIT_MAP = {
    "volt": "V", "v": "V",
    "watt": "W", "w": "W", "kw": "kW",
    "ampere": "A", "amp": "A", "a": "A",
    "hertz": "Hz", "hz": "Hz",
    "kwh": "kWh", "wh": "Wh", "mwh": "MWh",
    "var": "var", "kvar": "kvar",
    "va": "VA", "kva": "kVA",
    "varh": "varh", "kvarh": "kvarh",
}

_M = SensorStateClass.MEASUREMENT
_TI = SensorStateClass.TOTAL_INCREASING

# Neuere HA-Versionen haben mehr Klassen; fehlende werden uebersprungen.
_REACTIVE_POWER = getattr(SensorDeviceClass, "REACTIVE_POWER", None)
_APPARENT_POWER = getattr(SensorDeviceClass, "APPARENT_POWER", None)
_REACTIVE_ENERGY = getattr(SensorDeviceClass, "REACTIVE_ENERGY", None)

_BY_UNIT: dict[str, tuple[SensorDeviceClass | None, SensorStateClass | None]] = {
    "V": (SensorDeviceClass.VOLTAGE, _M),
    "A": (SensorDeviceClass.CURRENT, _M),
    "W": (SensorDeviceClass.POWER, _M),
    "kW": (SensorDeviceClass.POWER, _M),
    "Hz": (SensorDeviceClass.FREQUENCY, _M),
    "var": (_REACTIVE_POWER, _M),
    "kvar": (_REACTIVE_POWER, _M),
    "VA": (_APPARENT_POWER, _M),
    "kVA": (_APPARENT_POWER, _M),
    "kWh": (SensorDeviceClass.ENERGY, _TI),
    "Wh": (SensorDeviceClass.ENERGY, _TI),
    "MWh": (SensorDeviceClass.ENERGY, _TI),
    "varh": (_REACTIVE_ENERGY, _TI),
    "kvarh": (_REACTIVE_ENERGY, _TI),
}


def normalize_unit(unit: str | None) -> str | None:
    """Ausgeschriebene Einheit in HA-Symbol umwandeln (Volt -> V)."""
    if not unit or not unit.strip():
        return None
    unit = unit.strip()
    return _UNIT_MAP.get(unit.lower(), unit)


def classify_sensor(
    unit: str | None, name: str
) -> tuple[SensorDeviceClass | None, SensorStateClass | None]:
    """Device-/State-Class bestimmen: primaer ueber die Einheit, sonst ueber den Namen."""
    lname = name.lower()

    if "power factor" in lname:
        return SensorDeviceClass.POWER_FACTOR, _M

    device_class, state_class = _BY_UNIT.get(normalize_unit(unit) or "", (None, None))

    # Netto-/Saldo-Zaehler koennen sinken -> TOTAL statt TOTAL_INCREASING
    if state_class is _TI and any(w in lname for w in ("net", "balance", "saldo")):
        state_class = SensorStateClass.TOTAL

    if device_class is None:
        return None, None
    return device_class, state_class
