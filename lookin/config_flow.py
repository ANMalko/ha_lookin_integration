from typing import TYPE_CHECKING, Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE_ID, CONF_HOST, CONF_IP_ADDRESS, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import DiscoveryInfoType

from .const import DOMAIN, LOGGER
from .error import DeviceAlreadyConfigured, DeviceNotFound, NoUsableService
from .protocol import LookInHttpProtocol

if TYPE_CHECKING:
    from homeassistant.data_entry_flow import FlowResult

    from .models import Device

ADD_NEW_DEVICE_SCHEMA = vol.Schema({vol.Required(CONF_IP_ADDRESS): str})


class LookinFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore
    def __init__(self) -> None:
        self._host: Optional[str] = None
        self._name: Optional[str] = None
        self._device_id: Optional[str] = None

    async def async_step_zeroconf(
        self, discovery_info: DiscoveryInfoType
    ) -> Optional["FlowResult"]:
        uid: str = discovery_info["hostname"][: -len(".local.")]
        self._host = discovery_info["host"]

        if not uid:
            return self.async_abort(reason="no_uid")

        await self.async_set_unique_id(uid.upper())
        self._abort_if_unique_id_configured(
            updates={
                CONF_HOST: self._host,
            }
        )

        try:
            device = await self._validate_device(host=self._host)  # type: ignore
        except NoUsableService:
            return self.async_abort(reason="no_usable_service")
        except DeviceNotFound:
            return self.async_abort(reason="no_devices_found")
        except DeviceAlreadyConfigured:
            return self.async_abort(reason="already_configured")
        except Exception:  # noqa
            LOGGER.exception("Unexpected exception")
            return self.async_abort(reason="unknown")
        else:
            self._name = device.name

        return await self.async_step_device_name()

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> "FlowResult":
        errors: Dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_IP_ADDRESS]

            try:
                device = await self._validate_device(host=host)
            except NoUsableService:
                errors["base"] = "no_usable_service"
            except DeviceNotFound:
                errors["base"] = "no_devices_found"
            except DeviceAlreadyConfigured:
                errors["base"] = "already_configured"
            except Exception:  # noqa
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    device.id.upper(), raise_on_progress=False
                )

                self._name = device.name
                self._host = host
                self._device_id = device.id

                return await self.async_step_device_name()

        return self.async_show_form(
            step_id="user", data_schema=ADD_NEW_DEVICE_SCHEMA, errors=errors
        )

    async def _validate_device(self, host: str) -> "Device":
        lookin_protocol = LookInHttpProtocol(
            host=host, session=async_get_clientsession(self.hass)
        )

        device = await lookin_protocol.get_info()

        if device.id in self._async_current_ids():
            raise DeviceAlreadyConfigured

        return device

    async def async_step_device_name(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> "FlowResult":
        errors: Dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_NAME]
            lookin_protocol = LookInHttpProtocol(
                host=self._host, session=async_get_clientsession(self.hass)  # type: ignore
            )

            try:
                await lookin_protocol.update_device_name(name=name)
            except NoUsableService:
                errors["base"] = "no_usable_service"
            except DeviceNotFound:
                errors["base"] = "no_devices_found"
            except Exception:  # noqa
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                self._name = name

                return await self.async_step_discovery_confirm()

        return self.async_show_form(
            step_id="device_name",
            data_schema=vol.Schema({vol.Required(CONF_NAME, default=self._name): str}),
            errors=errors,
        )

    async def async_step_discovery_confirm(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> "FlowResult":
        if user_input is None:
            return self.async_show_form(
                step_id="discovery_confirm",
                description_placeholders={"name": self._name},
            )

        return self._create_entry()

    def _create_entry(self) -> "FlowResult":
        return self.async_create_entry(
            title=self._name,
            data=self._get_data(),
        )

    def _get_data(self) -> Dict[str, Any]:
        data = {
            CONF_NAME: self._name,
            CONF_HOST: self._host,
            CONF_DEVICE_ID: self._device_id,
        }

        return data
