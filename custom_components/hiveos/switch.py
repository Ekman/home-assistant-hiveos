"""Main entity that controls the miner"""
import logging
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers import entity_platform
from . import const, hiveos

_LOGGER = logging.getLogger(__name__)

SERVICES = [
    "worker_shutdown",
    "worker_upgrade",
]

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initial setup for the workers. Download and identify all workers."""
    data = hass.data[const.DOMAIN][config_entry.entry_id]

    async_add_entities([
        hiveos.HiveOsWorker(
            coord,
            coord.hiveos_api,
            coord.data
        ) for coord in data[const.COORDINATORS]
    ])

    platform = entity_platform.async_get_current_platform()

    for service in SERVICES:
        platform.async_register_entity_service(
            service,
            {},
            f"async_{service}",
        )

class HiveOsWorker(CoordinatorEntity, SwitchEntity):
    """Main entity to switch the worker on or off"""
    def __init__(
        self,
        coordinator,
        hiveos_api: hiveos.HiveOsApi,
        params: hiveos.HiveOsWorkerParams
    ):
        super().__init__(coordinator)
        self._hiveos_api = hiveos_api
        self._params = params

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
    def extra_state_attributes(self):
        """Extra attributes for the worker"""
        return {
            "farm_id": self._params["farm_id"],
            "id": self._params["unique_id"]
        }

    @property
    def device_info(self):
        """Device info for the worker"""
        # See: https://developers.home-assistant.io/docs/device_registry_index/
        return {
            "identifiers": {
                (const.DOMAIN, self._params["unique_id"])
            },
            "name": self._params["name"],
            "sw_version": self._params["version"]
        }

    @property
    def available(self) -> bool:
        """If the switch is connected to the cloud and ready for commands"""
        return (self._params["online"]
            and self._params["gpus_online"] + self._params["gpus_offline"] > 0)

    def _handle_coordinator_update(self):
        """
        Called by Home Assistant asking the vacuum to update to the latest state.
        Can contain IO code.
        """
        self._params = self.coordinator.data

        self.async_write_ha_state()

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
        await self._hiveos_api.worker_set_state(
            self._params["farm_id"],
            self._params["unique_id"],
            state
        )

    async def async_worker_shutdown(self):
        """Shutdown the worker."""
        _LOGGER.debug(
            "Calling shutdown on worker \"%s\", farm ID \"%s\" and unique ID \"%s\".",
            self.name,
            self._params["farm_id"],
            self._params["unique_id"]
        )

        if not self.available:
            _LOGGER.warning("Could not shutdown worker \"%s\" since it's not available.", self.name)
        else:
            await self._hiveos_api.worker_shutdown(
                self._params["farm_id"],
                self._params["unique_id"]
            )

    async def async_worker_upgrade(self):
        """Shutdown the worker."""
        _LOGGER.debug(
            "Calling upgrade on worker \"%s\", farm ID \"%s\" and unique ID \"%s\".",
            self.name,
            self._params["farm_id"],
            self._params["unique_id"]
        )

        if not self.available:
            _LOGGER.warning("Could not upgrade worker \"%s\" since it's not available.", self.name)
        elif not self._params["needs_upgrade"]:
            _LOGGER.info(
                "HiveOS reports that this worker is already at the latest version \"%s\".",
                self._params["version"]
            )
        else:
            await self._hiveos_api.worker_upgrade(
                self._params["farm_id"],
                self._params["unique_id"]
            )
