"""Control your HiveOS crypto miners using Home Assistant"""
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .switch import HiveOsWorker
from .const import DOMAIN
from .hiveos import HiveOsApi

async def async_setup_entry(hass, config_entry) -> bool:
    """Setup the integration after the config flow"""
    discovery_info = {
        CONF_ACCESS_TOKEN: config_entry.data[CONF_ACCESS_TOKEN],
        CONF_URL: config_entry.data[CONF_URL]
    }

    hass.helpers.discovery.load_platform("switch", DOMAIN, discovery_info, {})

    return True
