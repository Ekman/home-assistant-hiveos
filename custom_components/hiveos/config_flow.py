"""Initial user configuration for the integration"""
import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .hiveos import HiveOsApi
from .exceptions import HiveOsApiException

async def validate_auth(access_token: str, hass: core.HomeAssistant) -> None:
    """Validate that the provided access token is correct"""
    session = async_get_clientsession(hass)

    hiveos = HiveOsApi(session, access_token)

    await hiveos.get_farms()

class HiveOsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configuration flow"""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                access_token = user_input[CONF_ACCESS_TOKEN]

                await validate_auth(access_token, self.hass)

                return self.async_create_entry(title="Credentials", data=user_input)
            except HiveOsApiException:
                errors[CONF_ACCESS_TOKEN] = "auth"

        schema = vol.Schema({
            vol.Required(CONF_ACCESS_TOKEN): str
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
