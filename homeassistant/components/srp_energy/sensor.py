"""Support for SRP Energy Sensor."""
from datetime import datetime, timedelta

import async_timeout
from requests.exceptions import ConnectionError as ConnectError, HTTPError, Timeout

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, ENERGY_KILO_WATT_HOUR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ATTRIBUTION,
    CONF_IS_TOU,
    DEFAULT_NAME,
    DOMAIN,
    ICON,
    LOGGER,
    MIN_TIME_BETWEEN_UPDATES,
    SENSOR_NAME,
    SENSOR_TYPE,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the SRP Energy Usage sensor."""
    # API object stored here by __init__.py
    is_time_of_use: bool = getattr(entry, CONF_IS_TOU, False)
    api = hass.data[DOMAIN][entry.entry_id]

    LOGGER.debug("sensor: async_setup_entry apti: %s %s", type(api), api)

    async def async_update_data():
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        LOGGER.debug("sensor: async_update_data enter")
        try:
            # Fetch srp_energy data
            start_date = datetime.now() + timedelta(days=-1)
            end_date = datetime.now()

            async with async_timeout.timeout(10):
                hourly_usage = await hass.async_add_executor_job(
                    api.usage,
                    start_date,
                    end_date,
                    is_time_of_use,
                )

                LOGGER.debug(
                    "sensor: async_update_data: Received %s records from %s to %s",
                    len(hourly_usage) if hourly_usage else "None",
                    start_date,
                    end_date,
                )

                previous_daily_usage = 0.0
                for _, _, _, kwh, _ in hourly_usage:
                    previous_daily_usage += float(kwh)

                LOGGER.debug(
                    "sensor: async_update_data: previous_daily_usage %s",
                    previous_daily_usage,
                )

                return previous_daily_usage
        except (TimeoutError) as timeout_err:
            raise UpdateFailed("Timeout communicating with API") from timeout_err
        except (ConnectError, HTTPError, Timeout, ValueError, TypeError) as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name="sensor",
        update_method=async_update_data,
        update_interval=MIN_TIME_BETWEEN_UPDATES,
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    async_add_entities([SrpEntity(coordinator)])


class SrpEntity(SensorEntity):
    """Implementation of a Srp Energy Usage sensor."""

    _attr_should_poll = False

    def __init__(self, coordinator):
        """Initialize the SrpEntity class."""
        self._name = SENSOR_NAME
        self.type = SENSOR_TYPE
        self.coordinator = coordinator
        self._unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._state = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME} {self._name}"

    @property
    def unique_id(self) -> str:
        """Return sensor unique_id."""
        return self.type

    @property
    def native_value(self) -> StateType:
        """Return the state of the device."""
        if self._state:
            return f"{self._state:.2f}"
        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    @property
    def icon(self) -> str:
        """Return icon."""
        return ICON

    @property
    def usage(self) -> str:
        """Return entity state."""
        usage: float = 0.0
        if self.coordinator.data:
            usage = self.coordinator.data
        return f"{usage:.2f}"

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the state attributes."""
        attributes = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }

        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def device_class(self) -> str:
        """Return the device class."""
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self) -> str:
        """Return the state class."""
        return SensorStateClass.TOTAL_INCREASING

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
        if self.coordinator.data:
            self._state = self.coordinator.data

    async def async_update(self) -> None:
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self.coordinator.async_request_refresh()
