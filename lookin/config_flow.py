from homeassistant import config_entries
import voluptuous as vol
from homeassistant.const import CONF_DEVICE

from .const import DOMAIN, LOGGER


class LookinFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    def __init__(self):
        self.device_config = {}

    async def async_step_user(self, user_input=None):
        errors = {}
        LOGGER.debug("Lookin service config started")
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            LOGGER.debug("Lokin service config")

            device = user_input[CONF_DEVICE]

            self.device_config = {CONF_DEVICE: device}

            return self.async_create_entry(
                title=f"LookIn device controller - {user_input[CONF_DEVICE]}", data=user_input
            )

        # if user_input is None:
        #     return self.async_show_form(
        #         step_id="user", data_schema=vol.Schema(self.data_schema)
        #     )

        data_schema = {vol.Required(CONF_DEVICE, default=CONF_DEVICE): str}

        return self.async_show_form(
            step_id="user",
            description_placeholders=self.device_config,
            data_schema=vol.Schema(data_schema)
        )
