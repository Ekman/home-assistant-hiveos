"""Initial user configuration for the integration"""
import voluptuous as vol
from homeassistant import config_entries, core
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_URL
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .hiveos import HiveOsApi

async def validate_auth(access_token: str, url: str, hass: core.HomeAssistant) -> None:
    """Validate that the provided access token is correct"""
    session = async_get_clientsession(hass)

    hiveos = HiveOsApi(session, access_token, url)

    await hiveos.get_farms()

class HiveOsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configuration flow"""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            access_token = user_input[CONF_ACCESS_TOKEN]
            url = user_input[CONF_URL]

            await validate_auth(access_token, url, self.hass)

            return self.async_create_entry(title="HiveOS", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_ACCESS_TOKEN): cv.string,
            vol.Required(CONF_URL, default="https://api2.hiveos.farm/api/v2"): cv.string
        })

        return self.async_show_form(step_id="user", data_schema=schema)
