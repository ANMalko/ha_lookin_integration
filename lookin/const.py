import logging
from typing import Final

DOMAIN = "lookin"

DEVICE_INFO_URL: Final = "http://{host}/device"
METEO_SENSOR_URL: Final = "http://{host}/sensors/meteo"

LOGGER = logging.getLogger(__name__)
