"""The lookin integration remote platform."""
from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine, Iterable
from datetime import timedelta
import logging
from typing import Any

from aiolookin import IRFormat, Remote
from homeassistant.components.remote import ATTR_DELAY_SECS, RemoteEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .entity import LookinPowerEntity
from .models import LookinData

KNOWN_FORMAT_PREFIXES = {f"{format.value}:": format for format in IRFormat}

LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the light platform for lookin from a config entry."""
    lookin_data: LookinData = hass.data[DOMAIN][config_entry.entry_id]
    entities = []

    for remote in lookin_data.devices:
        if remote["Type"] != "00":
            continue
        uuid = remote["UUID"]

        def _wrap_async_update(
            uuid: str,
        ) -> Callable[[], Coroutine[None, Any, Remote]]:
            """Create a function to capture the uuid cell variable."""

            async def _async_update() -> Remote:
                return await lookin_data.lookin_protocol.get_remote(uuid)

            return _async_update

        coordinator = DataUpdateCoordinator(
            hass,
            LOGGER,
            name=f"{config_entry.title} {uuid}",
            update_method=_wrap_async_update(uuid),
            update_interval=timedelta(
                seconds=60
            ),  # Updates are pushed (fallback is polling)
        )
        await coordinator.async_refresh()
        device: Remote = coordinator.data

        entities.append(
            LookinRemoteEntity(
                uuid=uuid,
                device=device,
                lookin_data=lookin_data,
                coordinator=coordinator,
            )
        )

    async_add_entities(entities)


class LookinRemoteEntity(LookinPowerEntity, RemoteEntity, RestoreEntity):
    """Representation of a lookin remote."""

    def __init__(
        self,
        uuid: str,
        device: Remote,
        lookin_data: LookinData,
        coordinator: DataUpdateCoordinator,
    ) -> None:
        """Initialize the remote."""
        super().__init__(coordinator, uuid, device, lookin_data)
        self._attr_name = f"{self._lookin_device.name} Remote"
        self._attr_unique_id = self._lookin_device.id
        self._attr_is_on = True
        self._attr_supported_features = 0

    async def async_added_to_hass(self) -> None:
        """Call when the remote is added to hass."""
        state = await self.async_get_last_state()
        self._attr_is_on = state is None or state.state != STATE_OFF
        await super().async_added_to_hass()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the remote."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the remote."""
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_send_command(self, command: Iterable[str], **kwargs: Any) -> None:
        """Send a list of commands."""
        delay = kwargs.get(ATTR_DELAY_SECS)

        if not self._attr_is_on:
            raise HomeAssistantError(
                f"send_command canceled: {self.name} ({self.entity_id}) is turned off"
            )

        for idx, codes in enumerate(command):
            if idx and delay:
                await asyncio.sleep(delay)

            ir_format = None
            for prefix, ir_format_ in KNOWN_FORMAT_PREFIXES.items():
                if codes.startswith(prefix):
                    codes = codes[(len(prefix)):]
                    ir_format = ir_format_
                    break

            if not ir_format:
                raise HomeAssistantError(
                    f"Commands must be prefixed with one of {list(KNOWN_FORMAT_PREFIXES)}"
                )

            codes = codes.replace(",", " ")
            await self._lookin_protocol.send_ir(ir_format=ir_format, codes=codes)
