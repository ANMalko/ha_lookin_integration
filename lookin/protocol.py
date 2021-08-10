import json
from typing import TYPE_CHECKING

from aiohttp import ClientError

from .const import DEVICE_INFO_URL, METEO_SENSOR_URL
from .error import DeviceNotFound, NoUsableService
from .models import Device, MeteoSensor

if TYPE_CHECKING:
    from aiohttp import ClientResponse, ClientSession


async def validate_response(response: "ClientResponse") -> None:
    if response.status not in (200, 201, 204):
        raise NoUsableService


class LookInHttpProtocol:

    def __init__(self, host: str, session: "ClientSession"):
        self._host = host
        self._session = session

    async def get_device_info(self) -> Device:
        try:
            response = await self._session.get(
                url=DEVICE_INFO_URL.format(host=self._host)
            )
        except ClientError:
            raise DeviceNotFound

        async with response:
            await validate_response(response)
            payload = await response.json()

        return Device(device_info_dict=payload)

    async def update_device_name(self, name: str) -> None:
        try:
            response = await self._session.post(
                url=DEVICE_INFO_URL.format(host=self._host),
                data=json.dumps({"name": name})
            )
        except ClientError:
            raise DeviceNotFound

        async with response:
            await validate_response(response)

    async def get_meteo_sensor(self) -> MeteoSensor:
        try:
            response = await self._session.get(
                url=METEO_SENSOR_URL.format(host=self._host)
            )
        except ClientError:
            raise DeviceNotFound

        async with response:
            await validate_response(response)
            payload = await response.json()

        return MeteoSensor(meteo_sensor_dict=payload)
