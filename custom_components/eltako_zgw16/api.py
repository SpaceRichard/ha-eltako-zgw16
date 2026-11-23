"""API client for the Eltako ZGW16-IP gateway (REST)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)

_TIMEOUT = aiohttp.ClientTimeout(total=10)


class EltakoAuthError(Exception):
    """Login failed or token rejected."""


class EltakoApi:
    """API client for Eltako ZGW16-IP (ein Gateway, mehrere Zaehler)."""

    def __init__(self, host: str, password: str, session: ClientSession) -> None:
        self._host = host
        self._password = password
        self._session = session
        self._token: str | None = None
        self._login_lock = asyncio.Lock()
        self._register_names: dict[str, dict[str, str]] = {}

    # ---------- Auth ----------
    async def async_login(self) -> None:
        """Login and store access token."""
        url = f"http://{self._host}/api/login"
        _LOGGER.debug("Logging in to Eltako gateway")
        async with self._session.post(
            url, json={"login": {"password": self._password}}, timeout=_TIMEOUT
        ) as resp:
            if resp.status in (400, 401, 403):
                raise EltakoAuthError("Invalid credentials")
            resp.raise_for_status()
            data = await resp.json()
        try:
            self._token = data["login"]["accessToken"]
        except (KeyError, TypeError) as err:
            raise EltakoAuthError("No access token received") from err

    async def async_ensure_login(self) -> None:
        """Login only once, even if called concurrently."""
        if self._token:
            return
        async with self._login_lock:
            if not self._token:
                await self.async_login()

    # ---------- Requests ----------
    async def _request(self, path: str, retry: bool = True) -> Any:
        await self.async_ensure_login()
        url = f"http://{self._host}{path}"
        headers = {"accessToken": self._token}

        async with self._session.get(url, headers=headers, timeout=_TIMEOUT) as resp:
            if resp.status == 401:
                self._token = None
                if retry:
                    _LOGGER.debug("Token invalid, re-authenticating")
                    return await self._request(path, retry=False)
                raise EltakoAuthError("Token rejected after re-login")
            resp.raise_for_status()
            return await resp.json()

    async def async_get_devices(self) -> list[dict[str, Any]]:
        """Liste aller am Gateway angeschlossenen Zaehler."""
        data = await self._request("/api/devices")
        return data.get("devices", [])

    async def async_get_device_data(self, device_id: int) -> dict[str, Any]:
        """Live-Daten eines Zaehlers (device_id = busAddress)."""
        return await self._request(f"/api/devices/{device_id}")

    async def async_get_register_names(self, device_type_id: str) -> dict[str, str]:
        """Mapping register-nummer -> Name (gecacht)."""
        if device_type_id in self._register_names:
            return self._register_names[device_type_id]

        types = await self._request("/api/devices/types")
        for dt in types.get("deviceTypes", []):
            if dt.get("deviceTypeId") == device_type_id:
                mapping: dict[str, str] = {}
                for reg in dt.get("registers", []):
                    desc = reg.get("description") or [{}]
                    mapping[str(reg["number"])] = desc[0].get("en", str(reg["number"]))
                self._register_names[device_type_id] = mapping
                return mapping
        return {}
