from typing import TYPE_CHECKING, Any, Dict, Optional

from homeassistant.components.light import COLOR_MODE_ONOFF, LightEntity
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEVICES, DOMAIN, PROTOCOL
from .protocol import LookInHttpProtocol

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .models import Remote


async def async_setup_entry(
    hass: "HomeAssistant",
    config_entry: "ConfigEntry",
    async_add_entities: "AddEntitiesCallback",
) -> None:
    data = hass.data[DOMAIN][config_entry.entry_id]
    lookin_protocol = data[PROTOCOL]
    devices = data[DEVICES]

    entities = []

    for remote in devices:
        if remote["Type"] == "03":
            uuid = remote["UUID"]
            device = await lookin_protocol.get_remote(uuid)
            entities.append(
                LookinLight(uuid=uuid, lookin_protocol=lookin_protocol, device=device)
            )

    async_add_entities(entities, update_before_add=True)


class LookinLight(LightEntity):

    _attr_supported_color_modes = [COLOR_MODE_ONOFF]
    _attr_color_mode = COLOR_MODE_ONOFF
    _attr_should_poll = False

    def __init__(
        self, uuid: str, lookin_protocol: "LookInHttpProtocol", device: "Remote"
    ) -> None:
        self._uuid = uuid
        self._lookin_protocol = lookin_protocol
        self._device = device
        self._device_class = "Light"

        self._power_on_command: str = "power"
        self._power_off_command: str = "power"

        self._attr_unique_id = uuid

        self._is_on = False

        for function in self._device.functions:
            if function.name == "power":
                self._power_on_command = "power"
                self._power_off_command = "power"
            elif function.name == "poweron":
                self._power_on_command = "poweron"
            elif function.name == "poweroff":
                self._power_off_command = "poweroff"

    @property
    def name(self) -> str:
        return self._device.name

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._lookin_protocol.send_command(
            uuid=self._uuid, command=self._power_on_command, signal="FF"
        )
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._lookin_protocol.send_command(
            uuid=self._uuid, command=self._power_off_command, signal="FF"
        )
        self._is_on = False
        self.async_write_ha_state()

    @property
    def device_info(self) -> Dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self._device_class,
            "model": "Unavailable",
            "manufacturer": "Unavailable",
        }
