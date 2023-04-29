"""Coordinate data updates from Pure i9."""
import logging
from datetime import timedelta
import async_timeout
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from . import hiveos

_LOGGER = logging.getLogger(__name__)

class HiveOsCoordinator(DataUpdateCoordinator):
    """Coordinate data updates from HiveOs."""

    def __init__(
        self,
        hass,
        hiveos_api: hiveos.HiveOsApi,
        farm_id: int,
        worker_id: int
    ):
        super().__init__(
            hass,
            _LOGGER,
            name=f"{farm_id}_{worker_id}",
            update_interval=timedelta(minutes=1),
        )
        self._hiveos_api = hiveos_api
        self._farm_id = farm_id
        self._worker_id = worker_id

    @property
    def hiveos_api(self) -> hiveos.HiveOsApi:
        """Immutable HiveOsApi"""
        return self._hiveos_api

    async def _async_update_data(self):
        """Fetch data."""
        try:
            async with async_timeout.timeout(10):
                return await self.update_and_create_params()
        except Exception as ex:
            _LOGGER.error("Could not update data for \"%s\" due to: %s", self.name, ex)
            raise UpdateFailed from ex

    async def update_and_create_params(self) -> hiveos.HiveOsWorkerParams:
        """Update and create the latest version of params."""
        worker = await self._hiveos_api.get_worker(
            self._farm_id,
            self._worker_id
        )

        return {
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
            "online": worker["stats"]["online"],
            "needs_upgrade": worker["needs_upgrade"]
        }
