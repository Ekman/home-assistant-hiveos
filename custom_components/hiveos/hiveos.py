"""Interact with the HiveOS API"""
from typing import List, TypedDict, Optional
import logging
from aiohttp import ClientSession, ClientResponse
from .exceptions import HiveOsAipUnauthorizedException, HiveOsApiException

_LOGGER = logging.getLogger(__name__)

class HiveOsWorkerParams(TypedDict):
    """For easy reference of which params we use from the API"""
    unique_id: int
    name: str
    gpus_online: int
    gpus_offline: int
    farm_id: int
    version: str
    farm_name: str
    online: bool

class HiveOsCommand(TypedDict):
    """A HiveOs command"""
    command: str
    data: Optional[dict]

class HiveOsApi:
    """Interact with the HiveOS API"""

    def __init__(
        self,
        client: ClientSession,
        access_token: str,
        host: str = "https://api2.hiveos.farm/api/v2"
    ):
        self.client = client
        self.access_token = access_token
        self.host = host

    async def _request(self, method: str, path: str, body: dict = None) -> ClientResponse:
        """Execute a request to the API"""
        headers = {
            "authorization": f"Bearer {self.access_token}"
        }

        response = await self.client.request(
            method, f"{self.host}/{path}", json=body, headers=headers
        )

        if response.status == 401:
            raise HiveOsAipUnauthorizedException()

        body = await response.json()

        json = body["data"] if "data" in body else body

        if response.status > 299:
            raise HiveOsApiException(f"Failed response: {response.status} {json}")

        return json

    async def _command(
        self,
        farm_id: int,
        worker_id: int,
        command: HiveOsCommand
    ):
        """Alias to execute a command"""
        if "data" not in command:
            command["data"] = None

        _LOGGER.debug("Sending command: %s", command)

        return await self._request(
            "post",
            f"farms/{farm_id}/workers/{worker_id}/command",
            command
        )

    async def get_farms(self) -> List:
        """GET all farms"""
        return await self._request("get", "farms")

    async def get_workers(self, farm_id: int) -> List:
        """GET all workers from a farm"""
        return await self._request("get", f"farms/{farm_id}/workers")

    async def get_worker(self, farm_id: int, worker_id: int):
        """GET a specific worker from a farm"""
        return await self._request("get", f"farms/{farm_id}/workers/{worker_id}")

    async def worker_set_state(self, farm_id: int, worker_id: int, state: bool = True):
        """Set a worker to start/stop"""
        command = {
            "command": "miner",
            "data": {
                "action": "restart" if state else "stop"
            }
        }

        await self._command(farm_id, worker_id, command)

    async def worker_shutdown(self, farm_id: int, worker_id: int):
        """Shutdown a worker"""
        await self._command(farm_id, worker_id, {"command": "shutdown"})

    async def get_account_profile(self):
        """Get the account profile for the user with the associated access token."""
        return await self._request("get", "account/profile")

    async def worker_upgrade(self, farm_id: int, worker_id: int):
        """Upgrade the worker to the latest version"""
        await self._command(farm_id, worker_id, {"command": "upgrade"})
