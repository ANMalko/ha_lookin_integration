from typing import TYPE_CHECKING

from .const import DOMAIN, LOGGER, CONF_DEVICE

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: "HomeAssistant", config_entry: "ConfigEntry") -> bool:
    LOGGER.debug("Hello_service started")
    device = config_entry.data.get(CONF_DEVICE)
    LOGGER.debug("Hello_service test message, device <%s>", device)

    return True
