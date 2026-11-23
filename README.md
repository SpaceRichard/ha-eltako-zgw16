# Eltako ZGW16-IP für Home Assistant

> **Inoffizielle Integration.** Dieses Projekt wird nicht von der Eltako GmbH
> entwickelt, unterstützt oder empfohlen. „Eltako“ ist eine Marke der jeweiligen
> Inhaber und wird hier nur zur Bezeichnung der kompatiblen Hardware verwendet.
> Nutzung auf eigene Verantwortung.

Liest die Zähler eines **Eltako ZGW16-IP** (ZGW16WL-IP / ZGW16NI-IP) über die
lokale **REST-API** aus. Praktisch, wenn der MQTT-Zugang des Gateways bereits
belegt ist (z. B. durch den Energieversorger), denn die REST-API läuft parallel
dazu.

## Funktionen

- Ein Eintrag pro **Gateway**, jeder erkannte Zähler wird automatisch ein eigenes **Gerät**
- Neue Zähler am Gateway erscheinen ohne Neustart
- Einrichtung, Neuanmeldung (Reauth) und Neukonfiguration (IP/Passwort) über die Oberfläche
- Einstellbares Abfrageintervall (5 bis 300 Sekunden)
- Geräte-, Zustands- und Einheitenklassen für das Energie-Dashboard
- Diagnose-Download (Zugangsdaten werden geschwärzt)

## Voraussetzungen

- Home Assistant 2026.9 oder neuer
- Gateway im selben Netzwerk, Passwort am Gateway vergeben
- Die Zähler müssen am Gateway erkannt sein (Modbus-RTU-Einstellungen prüfen)

## Installation (HACS, benutzerdefiniertes Repository)

1. HACS → Integrationen → ⋮ → *Benutzerdefinierte Repositories*
2. Repository-URL eintragen, Kategorie *Integration*
3. „Eltako ZGW16-IP“ installieren, Home Assistant neu starten
4. Einstellungen → Geräte & Dienste → Integration hinzufügen → *Eltako ZGW16-IP*

## Hinweise

- Die Kommunikation mit dem Gateway läuft über unverschlüsseltes **HTTP** im lokalen Netz.
- Getestet mit dem Zählertyp DSZ15DZMOD. Rückmeldungen zu anderen Zählern sind willkommen (bitte Diagnose-Download anhängen).
- Die Daten werden abgefragt (Polling); die Integration ist rein lesend.

## Lizenz

MIT, siehe [LICENSE](LICENSE).

## English summary

Unofficial integration for the Eltako ZGW16-IP Modbus/MQTT gateway using its local
REST API. One config entry per gateway, every detected meter becomes a device.
Works alongside MQTT, which the gateway only supports for a single broker. Not
affiliated with Eltako GmbH.
