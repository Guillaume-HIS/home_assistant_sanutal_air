"""Platform for fan integration."""
import logging

from homeassistant.components.fan import SUPPORT_SET_SPEED, FanEntity

from homeassistant.const import ATTR_ENTITY_ID
import homeassistant.helpers.config_validation as cv

from . import SANUTAL_AIR_DEVICES

import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

ATTR_FROST_ACTIVE = "frost_active"
ATTR_FILTER_RESET = "filter_reset"

SANUTAL_AIR_FAN_DEVICES = 'sanutal_air_fan_devices'

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):

    """Set up the fan."""
    if SANUTAL_AIR_FAN_DEVICES not in hass.data:
        hass.data[SANUTAL_AIR_FAN_DEVICES] = []

    for device in hass.data[SANUTAL_AIR_DEVICES]:
        hass.data[SANUTAL_AIR_FAN_DEVICES].append(SanutalAirFan(device))

    async_add_entities(hass.data[SANUTAL_AIR_FAN_DEVICES])

class SanutalAirFan(FanEntity):

    def __init__(self, fan):
        """Initialize the fan."""
        self._fan = fan
        self._name = fan.name
        self._host = fan.host

        """Perform inital update of fan status."""
        self.async_update()
        self._fan_state = self._fan.state
        self._fan_speed = self._fan.speed
        self._frost_active = self._fan.frost_active
        self._filter_reset = self._fan.filter_reset

    @property
    def name(self):
        """Return the name of the fan."""
        return self._fan.name

    @property
    def state(self):
        """Return the fan state."""
        return self._fan.state

    @property
    def should_poll(self):
        """Enable polling of the device."""
        return True

    @property
    def percentage(self):
        """Return the current fan speed."""
        return self._fan.speed

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return 100

    @property
    def supported_features(self):
        """Return supported features."""
        return SUPPORT_SET_SPEED

    @property
    def is_on(self):
        """If the fan currently is on or off."""
        if self._fan.state is not None:
            return self._fan.state
        return None

    @property
    def extra_state_attributes(self):
        """Return device specific state attributes."""
        return {
            ATTR_FROST_ACTIVE: self._frost_active,
            ATTR_FILTER_RESET: self._filter_reset
        }

    async def async_update(self) -> None:
        """ Get latest data from fan."""
        await self.hass.async_add_executor_job(self._fan.update)
        self._frost_active = self._fan.frost_active
        self._filter_reset = self._fan.filter_reset

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        if percentage == 0:
            self.async_turn_off()
            return
        if not self._fan.state == 'on':
           self.async_turn_on()
        await self.hass.async_add_executor_job(self._fan.set_speed, percentage)
        self.async_write_ha_state()

    async def async_turn_on(
        self,
        speed: str = None,
        percentage: int = None,
        preset_mode: str = None,
        **kwargs,
    ) -> None:

        """Turn on the fan."""
        await self.hass.async_add_executor_job(self._fan.set_state_on)
        if percentage is None:
            return
        self.async_set_percentage(percentage)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the fan."""
        await self.hass.async_add_executor_job(self._fan.set_state_off)
