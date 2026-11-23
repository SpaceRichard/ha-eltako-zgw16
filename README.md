# Eltako ZGW16-IP for Home Assistant

🇩🇪 [Deutsch](#deutsch) · 🇬🇧 [English](#english)

---

<a id="deutsch"></a>
## 🇩🇪 Deutsch

> **Inoffizielle Integration.** Dieses Projekt wird nicht von der Eltako GmbH
> entwickelt, unterstützt oder empfohlen. „Eltako“ ist eine Marke der jeweiligen
> Inhaber und wird hier nur zur Bezeichnung der kompatiblen Hardware verwendet.
> Nutzung auf eigene Verantwortung.

Liest die Zähler eines **Eltako ZGW16-IP** (ZGW16WL-IP / ZGW16NI-IP) über die
lokale **REST-API** aus. Praktisch, wenn der MQTT-Zugang des Gateways bereits
belegt ist (z. B. durch den Energieversorger), denn die REST-API läuft parallel
dazu.

### Funktionen

- Ein Eintrag pro **Gateway**, jeder erkannte Zähler wird automatisch ein eigenes **Gerät**
- Neue Zähler am Gateway erscheinen ohne Neustart
- Einrichtung, Neuanmeldung (Reauth) und Neukonfiguration (IP/Passwort) über die Oberfläche
- Einstellbares Abfrageintervall (5 bis 300 Sekunden)
- Geräte-, Zustands- und Einheitenklassen für das Energie-Dashboard
- Diagnose-Download (Zugangsdaten werden geschwärzt)

### Voraussetzungen

- Home Assistant 2026.9 oder neuer
- Gateway im selben Netzwerk, Passwort am Gateway vergeben
- Die Zähler müssen am Gateway erkannt sein (Modbus-RTU-Einstellungen prüfen)

### Installation

#### Über HACS (empfohlen)

1. In Home Assistant **HACS** öffnen → oben rechts **⋮** → **Benutzerdefinierte Repositories**.
2. Als Repository `https://github.com/SpaceRichard/ha-eltako-zgw16` eintragen, Kategorie **Integration**, auf *Hinzufügen* klicken.
3. In HACS nach **Eltako ZGW16-IP** suchen, öffnen und **Installieren** wählen.
4. **Home Assistant neu starten** (Einstellungen → System → Neustart).

#### Manuell

1. Den Ordner `custom_components/eltako_zgw16` aus diesem Repository in das Verzeichnis `config/custom_components/` deiner Home-Assistant-Installation kopieren (inklusive der Unterordner `brand` und `translations`).
2. Home Assistant neu starten.

### Einrichtung

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen** und nach **Eltako ZGW16-IP** suchen.
2. Angaben eintragen:
   - **IP-Adresse oder Hostname** des Gateways (z. B. `192.168.1.50`)
   - **Passwort** des Gateways
   - **Abfrageintervall** in Sekunden (Standard 30, möglich 5 bis 300)
3. Mit *Absenden* bestätigen. Die Integration prüft den Login und liest die Zählerliste.

Danach erscheinen in **Einstellungen → Geräte & Dienste → Eltako ZGW16-IP**:

- ein Gerät für das **Gateway**
- je ein Gerät pro **Zähler** (benannt nach der `friendlyId`, falls vergeben, sonst nach dem Gerätetyp, jeweils mit der Bus-Adresse, z. B. „Haus (Bus 1)“)
- alle Messwerte als **Sensoren**, die du direkt im Energie-Dashboard verwenden kannst

> **Tipp:** Vergib am Gateway pro Zähler eine eindeutige `friendlyId` (max. 16 Zeichen), **bevor** du die Integration einrichtest. Dann bekommen Geräte und Entities sprechende Namen.

#### Später ändern

- **Abfrageintervall:** am Eintrag auf **Konfigurieren** klicken.
- **IP oder Passwort ändern:** am Eintrag über **⋮ → Neu konfigurieren**. Ein leeres Passwortfeld behält das bisherige.
- **Passwort ungültig:** Home Assistant fragt automatisch nach einer erneuten Anmeldung.
- **Neuer Zähler am Gateway:** wird beim nächsten Abruf automatisch als Gerät ergänzt.

#### Probleme?

- *Keine Verbindung:* IP-Adresse und Netzwerk prüfen, das Gateway muss von Home Assistant aus erreichbar sein.
- *Zähler fehlt:* Am Gateway müssen die Modbus-RTU-Einstellungen stimmen, sonst wird der Zähler nicht erkannt.
- *Fehler melden:* Am Eintrag über **⋮ → Diagnose herunterladen** die Datei erzeugen (Zugangsdaten sind geschwärzt) und im Issue-Tracker anhängen.

### Hinweise

- Die Kommunikation mit dem Gateway läuft über unverschlüsseltes **HTTP** im lokalen Netz.
- Getestet mit dem Zählertyp DSZ15DZMOD. Rückmeldungen zu anderen Zählern sind willkommen (bitte Diagnose-Download anhängen).
- Die Daten werden abgefragt (Polling); die Integration ist rein lesend.

### Lizenz

MIT, siehe [LICENSE](LICENSE).

---

<a id="english"></a>
## 🇬🇧 English

> **Unofficial integration.** This project is not developed, supported or
> endorsed by Eltako GmbH. "Eltako" is a trademark of its respective owners and
> is used here only to identify the compatible hardware. Use at your own risk.

Reads the meters of an **Eltako ZGW16-IP** gateway (ZGW16WL-IP / ZGW16NI-IP)
through its local **REST API**. Handy when the gateway's MQTT connection is
already taken (e.g. by your energy provider), because the REST API runs in
parallel to it.

### Features

- One config entry per **gateway**, every detected meter automatically becomes its own **device**
- New meters on the gateway show up without a restart
- Setup, re-authentication (reauth) and reconfiguration (IP/password) through the UI
- Adjustable polling interval (5 to 300 seconds)
- Device, state and unit classes for the Energy dashboard
- Diagnostics download (credentials are redacted)

### Requirements

- Home Assistant 2026.9 or newer
- Gateway on the same network, password set on the gateway
- The meters must be detected by the gateway (check the Modbus RTU settings)

### Installation

#### Via HACS (recommended)

1. In Home Assistant open **HACS** → top right **⋮** → **Custom repositories**.
2. Enter `https://github.com/SpaceRichard/ha-eltako-zgw16` as the repository, category **Integration**, and click *Add*.
3. Search for **Eltako ZGW16-IP** in HACS, open it and choose **Download**.
4. **Restart Home Assistant** (Settings → System → Restart).

#### Manual

1. Copy the folder `custom_components/eltako_zgw16` from this repository into the `config/custom_components/` directory of your Home Assistant installation (including the `brand` and `translations` subfolders).
2. Restart Home Assistant.

### Setup

1. Go to **Settings → Devices & services → Add integration** and search for **Eltako ZGW16-IP**.
2. Enter the details:
   - **IP address or hostname** of the gateway (e.g. `192.168.1.50`)
   - **Password** of the gateway
   - **Polling interval** in seconds (default 30, range 5 to 300)
3. Confirm with *Submit*. The integration tests the login and reads the meter list.

Afterwards you will find under **Settings → Devices & services → Eltako ZGW16-IP**:

- one device for the **gateway**
- one device per **meter** (named after its `friendlyId` if set, otherwise after the device type, always with the bus address, e.g. "House (Bus 1)")
- all measurements as **sensors**, which you can use directly in the Energy dashboard

> **Tip:** Give every meter a unique `friendlyId` (max. 16 characters) on the gateway **before** you set up the integration. Devices and entities then get meaningful names.

#### Changing things later

- **Polling interval:** click **Configure** on the entry.
- **Change IP or password:** on the entry use **⋮ → Reconfigure**. Leaving the password field empty keeps the current one.
- **Invalid password:** Home Assistant automatically asks you to sign in again.
- **New meter on the gateway:** is added automatically as a device on the next poll.

#### Troubleshooting

- *Cannot connect:* check the IP address and your network, the gateway must be reachable from Home Assistant.
- *Meter missing:* the Modbus RTU settings on the gateway must be correct, otherwise the meter is not detected.
- *Reporting a problem:* on the entry use **⋮ → Download diagnostics** (credentials are redacted) and attach the file to your issue.

### Notes

- Communication with the gateway uses unencrypted **HTTP** on your local network.
- Tested with the DSZ15DZMOD meter type. Feedback on other meters is welcome (please attach the diagnostics download).
- Data is polled; the integration is read-only.

### License

MIT, see [LICENSE](LICENSE).
