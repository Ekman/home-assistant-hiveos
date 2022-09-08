"""Main entity that controls the miner"""
from datetime import timedelta
from homeassistant.components.switch import SwitchEntity, PLATFORM_SCHEMA
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from .hiveos import HiveOsApi, HiveOsWorkerParams
from .const import DOMAIN

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ACCESS_TOKEN): cv.string,
    vol.Optional(CONF_URL, default="https://api2.hiveos.farm/api/v2"): cv.string
})

SCAN_INTERVAL = timedelta(minutes=5)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Initial setup for the workers. Download and identify all workers."""
    access_token = (discovery_info[CONF_ACCESS_TOKEN] if discovery_info is not None
        else config[CONF_ACCESS_TOKEN])
    url = (discovery_info[CONF_URL] if discovery_info is not None
        else config[CONF_URL])

    session = async_get_clientsession(hass)

    hiveos = HiveOsApi(session, access_token, url)

    farms = await hiveos.get_farms()

    worker_entities = []

    for farm in farms:
        workers = await hiveos.get_workers(farm["id"])

        for worker in workers:
            worker_entities.append(HiveOsWorker.create(hiveos, farm, worker))

    async_add_entities(worker_entities)

class HiveOsWorker(SwitchEntity):
    """Main entity to switch the worker on or off"""
    def __init__(self, hiveos: HiveOsApi, params: HiveOsWorkerParams):
        self._hiveos = hiveos
        self._params = params
        self._assumed_next_state = None

    @staticmethod
    def create(hiveos: HiveOsApi, farm, worker):
        """Create a new instance from API data"""
        params = {
            "unique_id": worker["id"],
            "name": worker["name"],
            "gpus_online": worker["stats"]["gpus_online"],
            "gpus_offline": worker["stats"]["gpus_offline"],
            "farm_id": worker["farm_id"],
            "version": worker["versions"]["hive"],
            "farm_name": farm["name"],
            "online": worker["stats"]["online"]
        }

        return HiveOsWorker(hiveos, params)

    @property
    def unique_id(self) -> str:
        """Unique identifier to the worker"""
        return self._params["unique_id"]

    @property
    def name(self) -> str:
        """Name of the worker"""
        return self._params["name"]

    @property
    def is_on(self):
        """Is the worker on?"""
        return self._params["gpus_online"] > 0

    @property
    def assumed_state(self) -> bool:
        """Assume the next state after sending a command"""
        return self._assumed_next_state is not None

    @property
    def extra_state_attributes(self):
        """Extra attributes for the worker"""
        return {
            "farm_name": self._params["farm_name"]
        }

    @property
    def device_info(self):
        """Device info for the worker"""
        # See: https://developers.home-assistant.io/docs/device_registry_index/
        return {
            "identifiers": {
                (DOMAIN, self._params["unique_id"])
            },
            "name": self._params["name"],
            "sw_version": self._params["version"]
        }

    @property
    def available(self) -> bool:
        """If the switch is connected to the cloud and ready for commands"""
        return (self._params["online"]
            and self._params["gpus_online"] + self._params["gpus_offline"] > 0)

    async def async_update(self):
        """Main update logic. Poll API and check state"""
        if self._assumed_next_state is not None:
            self._params["gpus_online"] = self._assumed_next_state
            self._assumed_next_state = None
        else:
            worker = await self._hiveos.get_worker(
                self._params["farm_id"],
                self._params["unique_id"]
            )

            self._params["gpus_online"] = worker["stats"]["gpus_online"]
            self._params["gpus_offline"] = worker["stats"]["gpus_offline"]
            self._params["online"] = worker["stats"]["online"]

    async def async_turn_on(self, **kwargs):
        """Turn the worker on"""
        if not self.is_on:
            await self._set_state(True)

    async def async_turn_off(self, **kwargs):
        """Turn the worker off"""
        if self.is_on:
            await self._set_state(False)

    async def _set_state(self, state: bool):
        """Set the worker to start/stop"""
        await self._hiveos.worker_set_state(
            self._params["farm_id"],
            self._params["unique_id"],
            state
        )

        self._assumed_next_state = 1
