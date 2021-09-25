from typing import TYPE_CHECKING, Any, Final, Optional

from homeassistant.components.fan import SUPPORT_OSCILLATE, FanEntity
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
from .protocol import LookInHttpProtocol

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .models import Remote


FAN_SUPPORT_FLAGS: Final = SUPPORT_OSCILLATE


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
        if device["Type"] == "07":
            entities.append(
                LookinFan(
                    uuid=device["UUID"],
                    lookin_protocol=lookin_protocol,
                )
            )
        elif device["Type"] == "04":
            entities.append(
                LookinHumidifier(
                    uuid=device["UUID"],
                    lookin_protocol=lookin_protocol,
                )
            )
        elif device["Type"] == "05":
            entities.append(
                LookinPurifier(
                    uuid=device["UUID"],
                    lookin_protocol=lookin_protocol,
                )
            )

    async_add_entities(entities, update_before_add=True)


class LookinFanBase(FanEntity):
    _attr_should_poll = False

    def __init__(
            self,
            uuid: str,
            lookin_protocol: "LookInHttpProtocol",
            device_class: str
    ) -> None:
        self._uuid = uuid
        self._lookin_protocol = lookin_protocol
        self._device: Optional["Remote"] = None
        self._device_class = device_class
        self._power_on_command: str = "power"
        self._power_off_command: str = "power"
        self._is_on = False
        self._attr_unique_id = uuid

    @property
    def name(self) -> str:
        return self._device.name

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(
        self, speed: str = None, percentage=None, preset_mode=None, **kwargs
    ) -> None:
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
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self._device_class,
            "model": "Unavailable",
            "manufacturer": "Unavailable",
        }


class LookinFan(LookinFanBase):
    def __init__(
            self,
            uuid: str,
            lookin_protocol: "LookInHttpProtocol"
    ) -> None:
        self._supported_features = FAN_SUPPORT_FLAGS
        self._oscillating: bool = False
        super().__init__(
            uuid=uuid, lookin_protocol=lookin_protocol, device_class="Fan"
        )

    @property
    def supported_features(self):
        return self._supported_features

    @property
    def oscillating(self) -> bool:
        return self._oscillating

    async def async_oscillate(self, oscillating: bool):
        await self._lookin_protocol.send_command(
            uuid=self._uuid, command="swing", signal="FF"
        )

        self._oscillating = oscillating
        self.async_write_ha_state()


class LookinHumidifier(LookinFanBase):
    def __init__(
            self,
            uuid: str,
            lookin_protocol: "LookInHttpProtocol"
    ) -> None:
        super().__init__(
            uuid=uuid,
            lookin_protocol=lookin_protocol,
            device_class="Humidifier"
        )

    @property
    def icon(self) -> str:
        return "mdi:water-percent"


class LookinPurifier(LookinFanBase):
    def __init__(
            self,
            uuid: str,
            lookin_protocol: "LookInHttpProtocol"
    ) -> None:
        super().__init__(
            uuid=uuid,
            lookin_protocol=lookin_protocol,
            device_class="Purifier"
        )

    @property
    def icon(self) -> str:
        return "mdi:water"
