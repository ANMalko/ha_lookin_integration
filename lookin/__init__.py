from typing import TYPE_CHECKING, Any, Optional

from homeassistant.const import CONF_DEVICE_ID, CONF_HOST, CONF_NAME
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: "HomeAssistant", entry: "ConfigEntry") -> bool:
    LOGGER.warning("Lookin service started")
    LOGGER.warning("config_entry.data - <%s>", entry.data)

    LOGGER.warning("Lookin service CONF_DEVICE_ID <%s>", entry.data[CONF_DEVICE_ID])
    LOGGER.warning("Lookin service CONF_HOST <%s>", entry.data[CONF_HOST])

    LOGGER.warning("Lookin service entry.entry_id <%s>", entry.entry_id)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        CONF_HOST: entry.data[CONF_HOST],
        CONF_DEVICE_ID: entry.data[CONF_DEVICE_ID],
        CONF_NAME: entry.data[CONF_NAME]
    }

    hass.config_entries.async_setup_platforms(entry, ["sensor"])


    # Forward the setup to the sensor platform.
    # hass.async_create_task(
    #     hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    # )

    return True


class LookinSensor(Entity):

    def __init__(
        self,
        device_id: str,
        device_name: str,
        unit_of_measurement: str
    ):
        """Initialize the sensor."""
        self.current_value: Optional[Any] = None
        self._device_id = device_id
        self._name = f"{DOMAIN}.{device_name}.{self.device_class}"
        self._unique_id = f"{device_id}-{self.device_class}"
        self._unit_of_measurement = unit_of_measurement
        self._is_available = True
        self._firmware: Optional[str] = None

    @property
    def name(self):
        """Return the name of the tsensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the entity."""
        return self.current_value

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def device_id(self):
        """Return the device id"""
        return self._device_id

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def available(self):
        """Return True if entity is available."""
        return self._is_available

    @property
    def device_info(self):
        return {
            "identifiers": {
                # device id are unique identifiers within a specific domain
                (DOMAIN, self.device_id)
            },
            "name": "LOOK.in Remote",
            "manufacturer": "LOOK.in",
            "model": "Remote",
            "sw_version": self._firmware,
            "via_device": (DOMAIN, self._device_id),
        }
