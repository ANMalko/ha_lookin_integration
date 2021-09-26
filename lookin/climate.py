from typing import TYPE_CHECKING, Any, Dict, Final, List, Optional

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MIDDLE,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_FAN_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    SWING_BOTH,
    SWING_OFF,
)
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_WHOLE, TEMP_CELSIUS

from .const import DEVICES, DOMAIN, PROTOCOL
from .protocol import LookInHttpProtocol

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .models import Climate

SUPPORT_FLAGS: int = SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE | SUPPORT_SWING_MODE

STATE_TO_HVAC_MODE: Dict[str, int] = {
    HVAC_MODE_OFF: 0,
    HVAC_MODE_AUTO: 1,
    HVAC_MODE_COOL: 2,
    HVAC_MODE_HEAT: 3,
    HVAC_MODE_DRY: 4,
    HVAC_MODE_FAN_ONLY: 5,
}

STATE_TO_FAN_MODE: Dict[str, int] = {
    FAN_AUTO: 0,
    FAN_LOW: 1,
    FAN_MIDDLE: 2,
    FAN_HIGH: 3,
}

STATE_TO_SWING_MODE: Dict[str, int] = {SWING_OFF: 0, SWING_BOTH: 1}

MIN_TEMP: Final = 16
MAX_TEMP: Final = 30
TEMP_OFFSET: Final = 16


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
        if remote["Type"] == "EF":
            uuid = remote["UUID"]
            device = await lookin_protocol.get_conditioner(uuid)
            entities.append(
                Conditioner(uuid=uuid, lookin_protocol=lookin_protocol, device=device)
            )

    async_add_entities(entities)


class Conditioner(ClimateEntity):
    _attr_supported_features: int = SUPPORT_FLAGS
    _attr_fan_modes: List[str] = [FAN_AUTO, FAN_LOW, FAN_MIDDLE, FAN_HIGH]
    _attr_swing_modes: List[str] = [SWING_OFF, SWING_BOTH]
    _attr_hvac_modes: List[str] = [
        HVAC_MODE_OFF,
        HVAC_MODE_AUTO,
        HVAC_MODE_COOL,
        HVAC_MODE_HEAT,
        HVAC_MODE_DRY,
        HVAC_MODE_FAN_ONLY,
    ]

    def __init__(
        self, uuid: str, lookin_protocol: "LookInHttpProtocol", device: "Climate"
    ) -> None:
        self._uuid = uuid
        self._lookin_protocol = lookin_protocol
        self._device = device

    @property
    def unique_id(self) -> str:
        return self._uuid

    @property
    def name(self) -> str:
        return self._device.name

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        if (mode := STATE_TO_HVAC_MODE.get(hvac_mode)) is None:
            return

        self._device.hvac_mode = mode

        await self._lookin_protocol.update_conditioner(
            extra=self._device.extra, status=self._make_status()
        )

    @property
    def temperature_unit(self) -> str:
        return TEMP_CELSIUS

    @property
    def min_temp(self) -> int:
        return MIN_TEMP

    @property
    def max_temp(self) -> int:
        return MAX_TEMP

    @property
    def current_temperature(self) -> Optional[int]:
        return self._device.temperature + TEMP_OFFSET

    @property
    def target_temperature(self) -> Optional[int]:
        return self._device.temperature + TEMP_OFFSET

    @property
    def target_temperature_step(self) -> int:
        return PRECISION_WHOLE

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temperature = kwargs.get(ATTR_TEMPERATURE)

        if temperature is None:
            return

        self._device.temperature = int(temperature - TEMP_OFFSET)

        await self._lookin_protocol.update_conditioner(
            extra=self._device.extra, status=self._make_status()
        )

    @property
    def fan_mode(self) -> Optional[str]:
        return self._attr_fan_modes[self._device.fan_mode]

    async def async_set_fan_mode(self, fan_mode: str) -> None:

        if (mode := STATE_TO_FAN_MODE.get(fan_mode)) is None:
            return

        self._device.fan_mode = mode

        await self._lookin_protocol.update_conditioner(
            extra=self._device.extra, status=self._make_status()
        )

    @property
    def swing_modes(self) -> List[str]:
        return self._attr_swing_modes

    @property
    def swing_mode(self) -> Optional[str]:
        return self._attr_swing_modes[self._device.swing_mode]

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        if (mode := STATE_TO_SWING_MODE.get(swing_mode)) is None:
            return

        self._device.swing_mode = mode

        await self._lookin_protocol.update_conditioner(
            extra=self._device.extra, status=self._make_status()
        )

    @property
    def hvac_mode(self) -> str:
        return self._attr_hvac_modes[self._device.hvac_mode]

    async def async_update(self) -> None:
        device = await self._lookin_protocol.get_conditioner(self._uuid)
        self._device = device

    @property
    def device_info(self) -> Dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": "Conditioner",
            "model": "Unavailable",
            "manufacturer": "Unavailable",
        }

    @staticmethod
    def _int_to_hex(i: int) -> str:
        return f"{i + TEMP_OFFSET:X}"[1]

    def _make_status(self) -> str:
        return (
            f"{self._device.hvac_mode}"
            f"{self._int_to_hex(self._device.temperature)}"
            f"{self._device.fan_mode}"
            f"{self._device.swing_mode}"
        )
