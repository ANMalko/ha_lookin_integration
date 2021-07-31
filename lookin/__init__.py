from typing import TYPE_CHECKING

from homeassistant.const import CONF_IP_ADDRESS

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: "HomeAssistant", config_entry: "ConfigEntry") -> bool:
    LOGGER.warning("Lookin service started")
    LOGGER.warning("config_entry - <%s>", config_entry.data)
    ip_address = config_entry.data.get(CONF_IP_ADDRESS)
    LOGGER.warning("Lookin service test message, ip_address <%s>", ip_address)

    return True