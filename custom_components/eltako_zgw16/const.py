"""Constants for the Eltako ZGW16-IP integration."""

DOMAIN = "eltako_zgw16"

CONF_HOST = "host"
CONF_PASSWORD = "password"
# Nur noch fuer bestehende Eintraege (Legacy): damit der urspruenglich
# konfigurierte Zaehler seine alten unique_ids/Device-Identifier behaelt
# (Historie, Energy-Dashboard). Neue Eintraege haben dieses Feld nicht.
CONF_DEVICE_ID = "device_id"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 30
