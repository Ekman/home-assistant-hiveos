"""Interact with the HiveOS API"""
from typing import List, TypedDict
from aiohttp import ClientSession, ClientResponse

class HiveOsWorkerParams(TypedDict):
    """For easy reference of which params we use from the API"""
    unique_id: int
    name: str
    state: bool
    farm_id: int
    version: str
    farm_name: str
    online: bool

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

        body = await response.json()

        return body["data"] if "data" in body else body

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
        params = {
            "command": "exec",
            "data": {
                "cmd": "miner " + ("start" if state else "stop")
            }
        }

        await self._request("post", f"farms/{farm_id}/workers/{worker_id}/command", params)
