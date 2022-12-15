"""Control your HiveOS crypto miners using Home Assistant"""
from homeassistant.const import Platform

async def async_setup_entry(hass, config_entry) -> bool:
    """Setup the integration after the config flow"""
    await hass.config_entries.async_forward_entry_setups(config_entry, [Platform.SWITCH])
    return True
