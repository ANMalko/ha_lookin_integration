from typing import TYPE_CHECKING, Any, Dict, Optional

from homeassistant.const import CONF_DEVICE_ID, CONF_HOST, CONF_NAME
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity

from .const import DEVICES, DOMAIN, LOGGER, PLATFORMS, PROTOCOL
from .error import DeviceNotFound
from .protocol import LookInHttpProtocol  # TODO: move protocol into a PyPI package

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: "HomeAssistant", entry: "ConfigEntry") -> bool:
    LOGGER.warning("Lookin service started")
    LOGGER.warning("config_entry.data - <%s>", entry.data)

    LOGGER.warning("Lookin service CONF_DEVICE_ID <%s>", entry.data[CONF_DEVICE_ID])
    LOGGER.warning("Lookin service CONF_HOST <%s>", entry.data[CONF_HOST])

    LOGGER.warning("Lookin service entry.entry_id <%s>", entry.entry_id)

    lookin_protocol = LookInHttpProtocol(
        host=entry.data[CONF_HOST], session=async_get_clientsession(hass)
    )

    try:
        devices = await lookin_protocol.get_devices()
    except DeviceNotFound as ex:
        raise ConfigEntryNotReady from ex

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        CONF_HOST: entry.data[CONF_HOST],
        CONF_DEVICE_ID: entry.data[CONF_DEVICE_ID],
        CONF_NAME: entry.data[CONF_NAME],
        DEVICES: devices,
        PROTOCOL: lookin_protocol,
    }

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


class LookinSensor(Entity):
    def __init__(
        self, device_id: str, device_name: str, unit_of_measurement: str
    ) -> None:
        self.current_value: Optional[Any] = None
        self._device_id = device_id
        self._name = f"{DOMAIN}.{device_name}.{self.device_class}"
        self._unique_id = f"{device_id}-{self.device_class}"
        self._unit_of_measurement = unit_of_measurement
        self._is_available = True
        self._firmware: Optional[str] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> Optional[Any]:
        return self.current_value

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def unit_of_measurement(self) -> str:
        return self._unit_of_measurement

    @property
    def available(self) -> bool:
        return self._is_available

    @property
    def device_info(self) -> Dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self.device_id)},
            "name": "LOOKin climate sensor",
            "manufacturer": "LOOKin",
            "model": "Remote",
            "sw_version": self._firmware,
            "via_device": (DOMAIN, self._device_id),
        }
