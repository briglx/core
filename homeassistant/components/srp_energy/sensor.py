"""Support for SRP Energy Sensor."""
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENERGY_KILO_WATT_HOUR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import ATTRIBUTION, DEFAULT_NAME, DOMAIN, LOGGER, SENSOR_NAME
from .coordinator import SrpCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the SRP Energy Usage sensor."""
    LOGGER.debug("Setup Sensor Entities")
    entry_unique_id: str = getattr(entry, "unique_id", DEFAULT_NAME)
    coordinator: SrpCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SrpEntity(
                coordinator=coordinator,
                entry_unique_id=entry_unique_id,
            )
        ]
    )


class SrpEntity(CoordinatorEntity[SrpCoordinator], SensorEntity):
    """Implementation of a Srp Energy Usage sensor."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: SrpCoordinator,
        entry_unique_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"{self.coordinator.name} {SENSOR_NAME}"
        self._attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attrs: dict[str, Any] = {}
        unique_id: str = f"{entry_unique_id}_energy_usage".lower()

        LOGGER.debug("Setting entity name %s", unique_id)
        self._attr_unique_id = unique_id

        self._attr_native_value = self.coordinator.data["energy_usage_this_month"]

    @property
    def native_value(self) -> StateType:
        """Return the state of the device."""
        LOGGER.debug(
            "Reading entity native_value %s at %s",
            self.coordinator.data["energy_usage_this_month"],
            dt_util.now(),
        )
        return self.coordinator.data["energy_usage_this_month"]
