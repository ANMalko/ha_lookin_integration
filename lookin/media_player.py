from typing import TYPE_CHECKING, Optional

from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import (
    SUPPORT_NEXT_TRACK, SUPPORT_PREVIOUS_TRACK, SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_STEP)
from homeassistant.const import CONF_HOST, STATE_PLAYING
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN
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
    config = hass.data[DOMAIN][config_entry.entry_id]
    lookin_protocol = LookInHttpProtocol(
        host=config[CONF_HOST], session=async_get_clientsession(hass)
    )

    entities = []

    for device in await lookin_protocol.get_devices():
        if device["Type"] in ("01", "02"):
            device_class = "tv" if device["Type"] == "01" else "media"
            entities.append(
                LookinMedia(
                    uuid=device["UUID"],
                    lookin_protocol=lookin_protocol,
                    device_class=device_class
                )
            )

    async_add_entities(entities, update_before_add=True)


class LookinMedia(MediaPlayerEntity):
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
        self._supported_features: int = 0
        self._power_on_command: str = "power"
        self._power_off_command: str = "power"

    @property
    def state(self) -> str:
        return STATE_PLAYING

    @property
    def name(self) -> str:
        return self._device.name

    @property
    def device_class(self):
        return self._device_class

    @property
    def unique_id(self) -> str:
        return self._uuid

    @property
    def supported_features(self) -> int:
        return self._supported_features

    async def async_volume_up(self) -> None:
        await self._lookin_protocol.send_command(
            uuid=self._uuid, command="volup", signal="FF"
        )

    async def async_volume_down(self) -> None:
        await self._lookin_protocol.send_command(
            uuid=self._uuid, command="voldown", signal="FF"
        )

    async def async_media_previous_track(self):
        await self._lookin_protocol.send_command(
            uuid=self._uuid, command="chdown", signal="FF"
        )

    async def async_media_next_track(self):
        await self._lookin_protocol.send_command(
            uuid=self._uuid, command="chup", signal="FF"
        )

    async def async_mute_volume(self, mute) -> None:
        await self._lookin_protocol.send_command(
            uuid=self._uuid, command="mute", signal="FF"
        )

    async def async_turn_off(self) -> None:
        await self._lookin_protocol.send_command(
            uuid=self._uuid, command=self._power_off_command, signal="FF"
        )

    async def async_turn_on(self) -> None:
        await self._lookin_protocol.send_command(
            uuid=self._uuid, command=self._power_on_command, signal="FF"
        )

    async def async_update(self) -> None:
        self._device = await self._lookin_protocol.get_remote(self._uuid)

        for function in self._device.functions:
            if function.name == "power":
                self._supported_features = self._supported_features | SUPPORT_TURN_ON | SUPPORT_TURN_OFF
                self._power_on_command = "power"
                self._power_off_command = "power"
            elif function.name == "poweron":
                self._supported_features = self._supported_features | SUPPORT_TURN_ON
                self._power_on_command = "poweron"
            elif function.name == "poweroff":
                self._supported_features = self._supported_features | SUPPORT_TURN_OFF
                self._power_off_command = "poweroff"
            elif function.name == "mute":
                self._supported_features = self._supported_features | SUPPORT_VOLUME_MUTE
            elif function.name == "volup":
                self._supported_features = self._supported_features | SUPPORT_VOLUME_STEP
            elif function.name == "chup":
                self._supported_features = self._supported_features | SUPPORT_NEXT_TRACK
            elif function.name == "chdown":
                self._supported_features = self._supported_features | SUPPORT_PREVIOUS_TRACK

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self._device_class,
            "model": "Unavailable",
            "manufacturer": "Unavailable",
        }
