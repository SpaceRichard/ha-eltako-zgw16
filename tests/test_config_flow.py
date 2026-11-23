"""Tests fuer den Config Flow (Setup)."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.eltako_zgw16.api import EltakoAuthError
from custom_components.eltako_zgw16.const import DOMAIN

USER_INPUT = {"host": "http://192.168.1.50/", "password": "secret", "scan_interval": 30}

LOGIN = "custom_components.eltako_zgw16.config_flow.EltakoApi.async_login"
DEVICES = "custom_components.eltako_zgw16.config_flow.EltakoApi.async_get_devices"
SETUP = "custom_components.eltako_zgw16.async_setup_entry"


async def _start(hass):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    return result


async def test_user_flow_success(hass):
    result = await _start(hass)
    with patch(LOGIN), patch(DEVICES, return_value=[]), patch(SETUP, return_value=True):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    # Schema und Slash werden aus dem Host entfernt
    assert result["data"] == {"host": "192.168.1.50", "password": "secret"}
    assert result["options"] == {"scan_interval": 30}


@pytest.mark.parametrize(
    ("side_effect", "error"),
    [(EltakoAuthError("bad"), "invalid_auth"), (OSError("down"), "cannot_connect")],
)
async def test_user_flow_errors(hass, side_effect, error):
    result = await _start(hass)
    with patch(LOGIN, side_effect=side_effect):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": error}
