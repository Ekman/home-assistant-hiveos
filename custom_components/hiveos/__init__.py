"""Control your HiveOS crypto miners using Home Assistant"""
import asyncio
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_ACCESS_TOKEN
from . import const, coordinator, hiveos

PLATFORMS = [Platform.SWITCH]

async def get_hiveos_workers(hiveos_api: hiveos.HiveOsApi):
    """Get all HiveOS workes"""
    farms = await hiveos_api.get_farms()

    workers = await asyncio.gather(
        *[hiveos_api.get_workers(farm["id"]) for farm in farms]
    )

    # Flatten
    return sum(workers)

async def async_setup_entry(hass, config_entry) -> bool:
    """Setup the integration after the config flow"""
    access_token = config_entry.data.get(CONF_ACCESS_TOKEN)
    session = async_get_clientsession(hass)

    hiveos_api = hiveos.HiveOsApi(session, access_token)

    workers = await get_hiveos_workers(hiveos_api)

    # Create the coordinators
    coords = [
        coordinator.HiveOsCoordinator(
            hass,
            hiveos_api,
            worker["farm_id"],
            worker["id"]
        ) for worker in workers
    ]

    await asyncio.gather(
        *[coord.async_config_entry_first_refresh() for coord in coords]
    )

    # Continue with setting up devices and entities
    hass.data.setdefault(const.DOMAIN, {})
    hass.data[const.DOMAIN][config_entry.entry_id] = {const.COORDINATORS: coords}

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True
