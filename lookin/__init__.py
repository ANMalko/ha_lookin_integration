from .const import DOMAIN, LOGGER, CONF_DEVICE


async def async_setup_entry(hass, config_entry) -> bool:
    device = config_entry.data.get(CONF_DEVICE)
    LOGGER.debug("Service started, device <%s>", device)

    return True
