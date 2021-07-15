import asyncio
from typing import TYPE_CHECKING, Optional

from homeassistant.const import CONF_IP_ADDRESS

from .const import (DOMAIN, LOGGER, UDP_DISCOVER, UDP_DISCOVER_TIMEOUT,
                    UDP_LOCAL_PORT, UDP_REMOTE_PORT)
from .protocol import open_datagram_endpoint

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from lookin.protocol import Endpoint


class LookInClient:
    def __init__(self, endpoint: "Endpoint", loop: Optional["AbstractEventLoop"] = None):
        self._loop = loop or asyncio.get_event_loop()
        self.endpoint = endpoint
        self.task = asyncio.create_task(self.discover(UDP_DISCOVER_TIMEOUT))
        self.device_pool = []

    def close(self):
        if not self.endpoint:
            self.endpoint.close()

    async def discover(self, sleep_timeout: int):
        while True:
            self.endpoint.send(UDP_DISCOVER)
            LOGGER.warning("Send UDP_DISCOVER")
            await asyncio.sleep(sleep_timeout)


async def async_setup_entry(hass: "HomeAssistant", config_entry: "ConfigEntry") -> bool:
    LOGGER.warning("Lookin service started")
    ip_address = config_entry.data.get(CONF_IP_ADDRESS)
    LOGGER.warning("Lookin service test message, ip_address <%s>", ip_address)

    endpoint = await open_datagram_endpoint(
        local_host="0.0.0.0",
        local_port=UDP_LOCAL_PORT,
        remote_host="255.255.255.255",
        remote_port=UDP_REMOTE_PORT
    )

    lookin_client = LookInClient(endpoint=endpoint)

    return True