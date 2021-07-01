from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN, LOGGER, CONF_DEVICE


class LookinFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(self, user_input=None):

        if user_input is not None:
            LOGGER.debug("Service break config")

        data_schema = {vol.Required(CONF_DEVICE): str}

        return self.async_show_form(step_id="init", data_schema=vol.Schema(data_schema))
