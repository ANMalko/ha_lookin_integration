from dataclasses import InitVar, dataclass, field
from typing import Dict, Optional

__all__ = ("Device", "MeteoSensor",)


@dataclass
class Device:
    type: str = field(init=False)
    mrdc: str = field(init=False)
    status: str = field(init=False)
    id: str = field(init=False)
    name: Optional[str] = field(init=False)
    time: int = field(init=False)
    timezone: int = field(init=False)
    powermode: str = field(init=False)
    currentvoltage: int = field(init=False)
    firmware: float = field(init=False)
    temperature: int = field(init=False)
    homekit: int = field(init=False)
    ecomode: bool = field(init=False)
    sensormode: int = field(init=False)
    device_info_dict: InitVar[Dict[str, str]]

    def __post_init__(self, device_info_dict: Dict[str, str]):
        self.type = device_info_dict["Type"]
        self.mrdc = device_info_dict["MRDC"]
        self.status = device_info_dict["Status"]
        self.id = device_info_dict["ID"].upper()
        self.name = device_info_dict["Name"]
        self.time = int(device_info_dict["Time"])
        self.timezone = int(device_info_dict["Timezone"])
        self.powermode = device_info_dict["PowerMode"]
        self.currentvoltage = int(device_info_dict["CurrentVoltage"])
        self.firmware = float(device_info_dict["Firmware"])
        self.temperature = int(device_info_dict["Temperature"])
        self.homekit = int(device_info_dict["HomeKit"])
        self.ecomode = device_info_dict["EcoMode"] == "on"
        self.sensormode = int(device_info_dict["SensorMode"])


@dataclass
class MeteoSensor:
    humidity: float = field(init=False)
    pressure: int = field(init=False)
    temperature: float = field(init=False)
    updated: int = field(init=False)
    meteo_sensor_dict: InitVar[Dict[str, str]]

    def __post_init__(self, meteo_sensor_dict: Dict[str, str]):
        self.humidity = float(meteo_sensor_dict["Humidity"])
        self.pressure = int(meteo_sensor_dict["Pressure"])
        self.temperature = float(meteo_sensor_dict["Temperature"])
        self.updated = int(meteo_sensor_dict["Updated"])
