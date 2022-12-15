"""Initial user configuration for the integration"""
import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .hiveos import HiveOsApi
from .exceptions import HiveOsAipUnauthorizedException

class HiveOsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configuration flow"""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                # Validate that the provided access token is correct
                session = async_get_clientsession(self.hass)
                hiveos = HiveOsApi(session, user_input[CONF_ACCESS_TOKEN])
                account_profile = await hiveos.get_account_profile()

                return self.async_create_entry(
                    title=account_profile["login"],
                    data=user_input
                )
            except HiveOsAipUnauthorizedException:
                errors[CONF_ACCESS_TOKEN] = "auth"

        schema = vol.Schema({
            vol.Required(CONF_ACCESS_TOKEN): str
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
