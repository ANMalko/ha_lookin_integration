from typing import TYPE_CHECKING, Final, Optional

from homeassistant.components.vacuum import (SERVICE_START, SERVICE_STOP,
                                             SUPPORT_TURN_OFF, SUPPORT_TURN_ON,
                                             VacuumEntity)
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .protocol import LookInHttpProtocol

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .models import Remote


SUPPORT_FLAGS: Final = (
        SUPPORT_TURN_ON |
        SUPPORT_TURN_OFF
)


async def async_setup_entry(
    hass: "HomeAssistant",
    config_entry: "ConfigEntry",
    async_add_entities: "AddEntitiesCallback",
) -> None:
    config = hass.data[DOMAIN][config_entry.entry_id]
    lookin_protocol = LookInHttpProtocol(
        host=config[CONF_HOST], session=async_get_clientsession(hass)
    )

    entities = []

    for device in await lookin_protocol.get_devices():
        if device["Type"] == "06":
            entities.append(
                LookinVacuum(
                    uuid=device["UUID"],
                    lookin_protocol=lookin_protocol,
                )
            )

    async_add_entities(entities, update_before_add=True)


class LookinVacuum(VacuumEntity):
    _attr_should_poll = False

    def __init__(self,  uuid: str, lookin_protocol: "LookInHttpProtocol"):
        self._uuid = uuid
        self._lookin_protocol = lookin_protocol
        self._device: Optional["Remote"] = None
        self._device_class = "Vacuum"

        self._power_on_command: str = "power"
        self._power_off_command: str = "power"

        self._attr_unique_id = uuid
        self._is_on = False
        self._status = SERVICE_STOP
        self._supported_features = SUPPORT_FLAGS

    @property
    def name(self) -> str:
        return self._device.name

    @property
    def supported_features(self):
        return self._supported_features

    @property
    def is_on(self):
        return self._status != SERVICE_STOP

    @property
    def status(self):
        return self._status

    async def async_turn_on(self, **kwargs):
        await self._lookin_protocol.send_command(
            uuid=self._uuid, command=self._power_on_command, signal="FF"
        )
        self._status = SERVICE_START
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._lookin_protocol.send_command(
            uuid=self._uuid, command=self._power_off_command, signal="FF"
        )
        self._status = SERVICE_STOP
        self.async_write_ha_state()

    async def async_update(self) -> None:
        self._device = await self._lookin_protocol.get_remote(self._uuid)

        for function in self._device.functions:
            if function.name == "power":
                self._power_on_command = "power"
                self._power_off_command = "power"
            elif function.name == "poweron":
                self._power_on_command = "poweron"
            elif function.name == "poweroff":
                self._power_off_command = "poweroff"

    @property
    def device_info(self):
        """Get attributes about the device."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self._device_class,
            "model": "Unavailable",
            "manufacturer": "Unavailable",
        }
