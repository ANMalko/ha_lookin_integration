from typing import TYPE_CHECKING

from homeassistant.const import CONF_DEVICE

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: "HomeAssistant", config_entry: "ConfigEntry") -> bool:
    LOGGER.warning("Lookin service started")
    device = config_entry.data.get(CONF_DEVICE)
    LOGGER.warning("Lookin service test message, device <%s>", device)

    return True