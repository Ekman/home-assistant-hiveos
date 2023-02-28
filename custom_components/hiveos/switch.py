"""Main entity that controls the miner"""
from datetime import timedelta
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import entity_platform
from .hiveos import HiveOsApi, HiveOsWorkerParams
from .const import DOMAIN

SCAN_INTERVAL = timedelta(minutes=1)

_LOGGER = logging.getLogger(__name__)

SERVICE_WORKER_SHUTDOWN = "worker_shutdown"

async def get_hiveos_farms_create_entities(hiveos_client):
    """Get all HiveOS farms and create entities from them"""
    farms = await hiveos_client.get_farms()
    worker_entities = []

    for farm in farms:
        workers = await hiveos_client.get_workers(farm["id"])

        for worker in workers:
            worker_entities.append(HiveOsWorker.create(hiveos_client, farm, worker))

    return worker_entities

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initial setup for the workers. Download and identify all workers."""
    access_token = config_entry.data.get(CONF_ACCESS_TOKEN)
    session = async_get_clientsession(hass)

    hiveos_client = HiveOsApi(session, access_token)

    async_add_entities(
        await get_hiveos_farms_create_entities(hiveos_client)
    )

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_WORKER_SHUTDOWN,
        {},
        "async_worker_shutdown",
    )

class HiveOsWorker(SwitchEntity):
    """Main entity to switch the worker on or off"""
    def __init__(self, hiveos_client: HiveOsApi, params: HiveOsWorkerParams):
        self._hiveos_client = hiveos_client
        self._params = params
        self._assumed_next_state = None

    @staticmethod
    def create(hiveos: HiveOsApi, farm, worker):
        """Create a new instance from API data"""
        params = {
            "unique_id": worker["id"],
            "name": worker["name"],
            "gpus_online": (
                worker["stats"]["gpus_online"]
                if "stats" in worker and "gpus_online" in worker["stats"]
                else 0
            ),
            "gpus_offline": (
                worker["stats"]["gpus_offline"]
                if "stats" in worker and "gpus_offline" in worker["stats"]
                else 0
            ),
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
            worker = await self._hiveos_client.get_worker(
                self._params["farm_id"],
                self._params["unique_id"]
            )

            self._params["gpus_online"] = (
                worker["stats"]["gpus_online"]
                if "stats" in worker and "gpus_online" in worker["stats"]
                else 0
            )
            self._params["gpus_offline"] = (
                worker["stats"]["gpus_offline"]
                if "stats" in worker and "gpus_offline" in worker["stats"]
                else 0
            )
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
        await self._hiveos_client.worker_set_state(
            self._params["farm_id"],
            self._params["unique_id"],
            state
        )

        self._assumed_next_state = 1

    async def async_worker_shutdown(self):
        """Shutdown the worker."""
        _LOGGER.debug("Calling shutdown on worker \"%s\", farm ID \"%s\" and unique ID \"%s\".", self.name, self._params["farm_id"], self._params["unique_id"])

        if not self.available:
            _LOGGER.warning("Could not shutdown worker \"%s\" since it's not available.", self.name)
        else:
            await self._hiveos_client.worker_shutdown(
                self._params["farm_id"],
                self._params["unique_id"]
            )
