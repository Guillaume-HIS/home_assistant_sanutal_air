"""Support for Sanutal Air ventilation system"""
import logging

import voluptuous as vol
from datetime import timedelta

from homeassistant.const import CONF_NAME, CONF_IP_ADDRESS, CONF_DEVICES
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'sanutal_air'
SANUTAL_AIR_DEVICES = 'sanutal_air_devices'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICES, default=[]): vol.All(cv.ensure_list, [dict]),
    })
},extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    """Set up the Sanutal Air component."""
    from sanutal_air import Ventilation

    if SANUTAL_AIR_DEVICES not in hass.data:
        hass.data[SANUTAL_AIR_DEVICES] = []

    conf = config[DOMAIN]
    conf_devices = config[DOMAIN].get(CONF_DEVICES)
    for device in conf_devices:
        name = device.get(CONF_NAME)
        ip_address = device.get(CONF_IP_ADDRESS)

        fan = Ventilation(ip_address, name)
        hass.data[SANUTAL_AIR_DEVICES].append(fan)

    hass.async_create_task(
        async_load_platform(hass, 'fan', DOMAIN, {CONF_NAME: DOMAIN}, config)
    )

    return True