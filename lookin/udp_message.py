from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Final, Optional

__all__ = ("UDPAlive", "UDPUpdate")


class DeviceType(Enum):
    remote = auto()
    unknown = auto()


device_type_mapping: Final = {"81": DeviceType.remote}


@dataclass
class UDPAlive:
    id: str
    device_type_hex: str = field(repr=False)
    device_type: DeviceType = field(init=False)
    batteries: bool
    ip: str
    version: str
    storage: str

    def __post_init__(self):
        self.device_type = device_type_mapping.get(
            self.device_type_hex, DeviceType.unknown)


@dataclass
class UDPUpdate:
    id: str
    sensor: str
    event: str
    value: str = field(repr=False)
    temperature: Optional[float] = None
    humidity: Optional[float] = None

    def __post_init__(self):
        if len(self.value) == 8:
            self.temperature = int(self.value[:4], 16)/10
            self.humidity = int(self.value[4:], 16) / 10
