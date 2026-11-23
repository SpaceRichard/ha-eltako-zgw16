"""Config flow for Eltako ZGW16-IP (Setup, Reauth, Reconfigure)."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import EltakoApi, EltakoAuthError
from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
from .options_flow import EltakoZgw16OptionsFlowHandler

_PASSWORD_SELECTOR = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))


def _clean_host(host: str) -> str:
    """Entfernt Leerzeichen, Schema und abschliessenden Slash."""
    host = host.strip()
    for prefix in ("http://", "https://"):
        if host.lower().startswith(prefix):
            host = host[len(prefix):]
    return host.rstrip("/")


async def _async_validate(hass: HomeAssistant, host: str, password: str) -> str | None:
    """Testet Login und Geraeteliste. Gibt einen Fehlerschluessel oder None zurueck."""
    api = EltakoApi(host, password, async_get_clientsession(hass))
    try:
        await api.async_login()
        await api.async_get_devices()
    except EltakoAuthError:
        return "invalid_auth"
    except Exception:  # noqa: BLE001
        return "cannot_connect"
    return None


class EltakoZgw16ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Eltako ZGW16-IP (pro Gateway ein Eintrag)."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            host = _clean_host(user_input[CONF_HOST])
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            error = await _async_validate(self.hass, host, user_input[CONF_PASSWORD])
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(
                    title="Eltako ZGW16-IP",
                    data={CONF_HOST: host, CONF_PASSWORD: user_input[CONF_PASSWORD]},
                    options={CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL]},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PASSWORD): _PASSWORD_SELECTOR,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): vol.All(int, vol.Range(min=5, max=300)),
                }
            ),
            errors=errors,
        )

    # ---------- Reauth: Passwort ungueltig ----------
    async def async_step_reauth(self, entry_data: dict[str, Any]):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None):
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            error = await _async_validate(
                self.hass, entry.data[CONF_HOST], user_input[CONF_PASSWORD]
            )
            if error:
                errors["base"] = error
            else:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_PASSWORD: user_input[CONF_PASSWORD]}
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): _PASSWORD_SELECTOR}),
            errors=errors,
            description_placeholders={"host": entry.data[CONF_HOST]},
        )

    # ---------- Reconfigure: IP/Hostname oder Passwort aendern ----------
    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            host = _clean_host(user_input[CONF_HOST])
            password = user_input.get(CONF_PASSWORD) or entry.data[CONF_PASSWORD]

            if any(
                other.entry_id != entry.entry_id and other.unique_id == host
                for other in self._async_current_entries()
            ):
                errors["base"] = "already_configured"
            else:
                error = await _async_validate(self.hass, host, password)
                if error:
                    errors["base"] = error
                else:
                    return self.async_update_reload_and_abort(
                        entry,
                        unique_id=host,
                        data_updates={CONF_HOST: host, CONF_PASSWORD: password},
                    )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): str,
                    vol.Optional(CONF_PASSWORD): _PASSWORD_SELECTOR,
                }
            ),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return EltakoZgw16OptionsFlowHandler(config_entry)
