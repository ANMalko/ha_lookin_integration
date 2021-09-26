import logging
from typing import Final

DOMAIN = "lookin"

INFO_URL: Final = "http://{host}/device"
METEO_SENSOR_URL: Final = "http://{host}/sensors/meteo"
DEVICES_INFO_URL: Final = "http://{host}/data"
DEVICE_INFO_URL: Final = "http://{host}/data/{uuid}"
UPDATE_CLIMATE_URL: Final = "http://{host}/commands/ir/ac/{extra}{status}"
SEND_IR_COMMAND: Final = "http://{host}/commands/ir/localremote/{uuid}{command}{signal}"

LOGGER = logging.getLogger(__name__)

DEVICES = "devices"
PROTOCOL = "protocol"

PLATFORMS = ["sensor", "climate", "media_player", "light", "vacuum", "fan"]
