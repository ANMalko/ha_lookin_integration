import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.helpers.typing import DiscoveryInfoType

from .const import DOMAIN, LOGGER


class LookinFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):

    def __init__(self):
        self.device_config = {}

    async def async_step_zeroconf(self, discovery_info: DiscoveryInfoType):
        LOGGER.warning("Lookin service zeroconf started")
        LOGGER.warning("discovery_info - <%s>", discovery_info)
        return self.async_show_form(
            step_id="discovery_confirm", description_placeholders={"name": "lookin device"}
        )

    async def async_step_user(self, user_input=None):
        errors = {}
        LOGGER.warning("Lookin service config started")
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            LOGGER.warning("Lokin service config")

            device = user_input[CONF_IP_ADDRESS]

            self.device_config = {CONF_IP_ADDRESS: device}

            return self.async_create_entry(
                title=f"LookIn device controller - {user_input[CONF_IP_ADDRESS]}", data=user_input
            )

        LOGGER.warning("Lokin service config show_form")
        data_schema = {vol.Required(CONF_IP_ADDRESS, default=CONF_IP_ADDRESS): str}

        return self.async_show_form(
            step_id="user",
            description_placeholders=self.device_config,
            data_schema=vol.Schema(data_schema)
        )
