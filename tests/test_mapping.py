"""Tests fuer Einheiten- und Klassen-Zuordnung."""

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass

from custom_components.eltako_zgw16.mapping import classify_sensor, normalize_unit


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Volt", "V"),
        ("Watt", "W"),
        ("Ampere", "A"),
        ("A", "A"),
        ("kWh", "kWh"),
        ("", None),
        (None, None),
        ("  ", None),
        ("Unbekannt", "Unbekannt"),
    ],
)
def test_normalize_unit(raw, expected):
    assert normalize_unit(raw) == expected


@pytest.mark.parametrize(
    ("unit", "name", "device_class", "state_class"),
    [
        ("Volt", "Voltage of L1 to N", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
        ("A", "L1 Current", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
        ("Watt", "L1 active power", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
        ("Hz", "Frequency", SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT),
        ("kWh", "Imported active energy", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        ("kWh", "Net active energy", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL),
        (None, "Total power factor", SensorDeviceClass.POWER_FACTOR, SensorStateClass.MEASUREMENT),
        ("", "Something else", None, None),
    ],
)
def test_classify_sensor(unit, name, device_class, state_class):
    assert classify_sensor(unit, name) == (device_class, state_class)
