from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_DEVICE_ID, CONF_HOST, CONF_NAME,
                                 CONF_OFFSET, DEVICE_CLASS_HUMIDITY,
                                 DEVICE_CLASS_TEMPERATURE, DEVICE_DEFAULT_NAME,
                                 PERCENTAGE, TEMP_CELSIUS)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import LookinSensor
from .const import DOMAIN, LOGGER
from .error import DeviceNotFound, NoUsableService
from .protocol import LookInHttpProtocol

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

CONF_SCALE = "scale"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEVICE_DEFAULT_NAME): vol.Coerce(str),
        vol.Optional(CONF_SCALE, default=1): vol.Coerce(float),
        vol.Optional(CONF_OFFSET, default=0): vol.Coerce(float),
    }
)


async def async_setup_entry(
    hass: "HomeAssistant",
    config_entry: "ConfigEntry",
    async_add_entities: "AddEntitiesCallback",
) -> None:
    LOGGER.warning("config - <%s>", hass.data[DOMAIN][config_entry.entry_id])

    config = hass.data[DOMAIN][config_entry.entry_id]

    LOGGER.warning("config[CONF_HOST] - <%s>", config[CONF_HOST])

    lookin_protocol = LookInHttpProtocol(
        host=config[CONF_HOST], session=async_get_clientsession(hass)
    )

    sensors = [
        TemperSensor(
            lookin_protocol=lookin_protocol,
            unit_of_measurement=TEMP_CELSIUS,
            device_id=config[CONF_DEVICE_ID],
            device_name=config[CONF_NAME]),
        HumiditySensor(
            lookin_protocol=lookin_protocol,
            unit_of_measurement=PERCENTAGE,
            device_id=config[CONF_DEVICE_ID],
            device_name=config[CONF_NAME])
    ]

    async_add_entities(sensors, update_before_add=True)


class TemperSensor(LookinSensor):

    def __init__(
        self,
        lookin_protocol: LookInHttpProtocol,
        device_id: str,
        device_name: str,
        unit_of_measurement: str,
    ):
        self._lookin_protocol = lookin_protocol
        super().__init__(
            device_id=device_id,
            device_name=device_name,
            unit_of_measurement=unit_of_measurement
        )

    @property
    def device_class(self):
        return DEVICE_CLASS_TEMPERATURE

    async def async_update(self):
        try:
            meteo_data = await self._lookin_protocol.get_meteo_sensor()
            device = await self._lookin_protocol.get_info()
        except NoUsableService:
            self._is_available = False
            LOGGER.error("No usable service")
        except DeviceNotFound:
            self._is_available = False
            LOGGER.error("No device found")
        except Exception:  # pylint: disable=broad-except
            self._is_available = False
            LOGGER.exception("Unexpected exception")
        else:
            self.current_value = meteo_data.temperature
            self._firmware = device.firmware
            self._is_available = True


class HumiditySensor(LookinSensor):

    def __init__(
        self,
        lookin_protocol: LookInHttpProtocol,
        device_id: str,
        device_name: str,
        unit_of_measurement: str,
    ):
        self._lookin_protocol = lookin_protocol
        super().__init__(
            device_id=device_id,
            device_name=device_name,
            unit_of_measurement=unit_of_measurement
        )

    @property
    def device_class(self):
        return DEVICE_CLASS_HUMIDITY

    async def async_update(self):
        try:
            meteo_data = await self._lookin_protocol.get_meteo_sensor()
        except NoUsableService:
            self._is_available = False
            LOGGER.error("No usable service")
        except DeviceNotFound:
            self._is_available = False
            LOGGER.error("No device found")
        except Exception:  # pylint: disable=broad-except
            self._is_available = False
            LOGGER.exception("Unexpected exception")
        else:
            self.current_value = meteo_data.humidity
            self._is_available = True