import json
from typing import TYPE_CHECKING

from aiohttp import ClientError
from homeassistant import core
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEVICE_INFO_URL
from .error import DeviceNotFound, NoUsableService
from .models import Device

if TYPE_CHECKING:
    from aiohttp import ClientResponse


async def validate_response(response: "ClientResponse") -> None:
    if response.status not in (200, 201, 204):
        raise NoUsableService


class LookInHttpProtocol:

    def __init__(self, host: str, hass: core.HomeAssistant):
        self._host = host
        self._http_session = async_get_clientsession(hass)

    async def get_device_info(self) -> Device:
        try:
            response = await self._http_session.get(
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
            response = await self._http_session.post(
                url=DEVICE_INFO_URL.format(host=self._host),
                data=json.dumps({"name": name})
            )
        except ClientError:
            raise DeviceNotFound

        async with response:
            await validate_response(response)
