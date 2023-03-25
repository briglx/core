"""Tests for Srp Energy component Init."""
from homeassistant.components.srp_energy import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant


async def test_setup_entry(hass: HomeAssistant, init_integration) -> None:
    """Test setup entry."""
    assert init_integration.state == ConfigEntryState.LOADED


async def test_unload_entry(hass: HomeAssistant, init_integration) -> None:
    """Test being able to unload an entry."""
    assert init_integration.state == ConfigEntryState.LOADED

    await hass.config_entries.async_unload(init_integration.entry_id)
    await hass.async_block_till_done()

    assert init_integration.entry_id not in hass.data[DOMAIN]
