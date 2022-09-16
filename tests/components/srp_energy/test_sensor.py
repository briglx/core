"""Tests for the srp_energy sensor platform."""
from datetime import timedelta

from freezegun.api import FrozenDateTimeFactory

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.srp_energy import ATTRIBUTION, DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import ENERGY_KILO_WATT_HOUR
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import TEST_DATE, TEST_SENSOR_COUNT

from tests.common import MockConfigEntry, async_fire_time_changed

GUID_LENGTH = 32


async def test_loading_sensors(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Test the srp energy sensors."""
    # Validate the Config Entry was initialized
    assert init_integration.state == ConfigEntryState.LOADED
    assert hass.data[DOMAIN]

    # Check sensors were loaded
    assert len(hass.states.async_all()) == TEST_SENSOR_COUNT


async def test_total_energy_sensors(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
) -> None:
    """Test the total energy sensor."""
    # Test Total Energy Entity
    sensor_entity_id = "sensor.test_home_energy_usage"

    # Validate the Config Entry was initialized
    assert init_integration.state == ConfigEntryState.LOADED
    assert hass.data[DOMAIN]

    # Check Entity Registry
    entity_registry = er.async_get(hass)
    er_entries = er.async_entries_for_config_entry(
        entity_registry, config_entry_id=init_integration.entry_id
    )
    assert er_entries is not None
    assert len(er_entries) > 0
    entity_entry = er_entries[0]
    assert entity_entry.entity_id == sensor_entity_id
    assert entity_entry.unique_id == "123456789_energy_usage"
    assert entity_entry.original_name == "Test Home Energy Usage"
    assert len(entity_entry.id) == GUID_LENGTH
    assert entity_entry.name is None

    # Check Sensor Entity State
    sensor = hass.states.get(sensor_entity_id)
    assert sensor is not None
    assert sensor.entity_id == sensor_entity_id
    assert sensor.name == "Test Home Energy Usage"
    assert sensor.state == "69.4"
    assert sensor.attributes["device_class"] == SensorDeviceClass.ENERGY
    assert sensor.attributes["state_class"] == SensorStateClass.TOTAL_INCREASING
    assert sensor.attributes["unit_of_measurement"] == ENERGY_KILO_WATT_HOUR
    assert sensor.attributes["attribution"] == ATTRIBUTION
    assert sensor.attributes["friendly_name"] == "Test Home Energy Usage"


async def test_data_update_invalid_dates(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mock_config_entry,
    mock_srp_energy,
) -> None:
    """Test the sensors data update with bad dates."""
    # Need to mock side effect on mock_srp_energy.
    # Can't use init_integration
    sensor_entity_id = "sensor.test_home_energy_usage"

    freezer.move_to(TEST_DATE)
    mock_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state == ConfigEntryState.LOADED
    assert hass.data[DOMAIN]

    assert len(hass.states.async_all()) == TEST_SENSOR_COUNT

    sensor = hass.states.get(sensor_entity_id)
    assert sensor is not None

    mock_srp_energy.usage.side_effect = ValueError

    # Test fetching new data
    future = TEST_DATE + timedelta(hours=9)
    async_fire_time_changed(hass, future)
    await hass.async_block_till_done()

    sensor = hass.states.get(sensor_entity_id)
    assert sensor is not None
    assert sensor.state == "69.4"


# async def test_async_setup_entry(hass):
#     """Test the sensor."""
#     fake_async_add_entities = MagicMock()
#     fake_srp_energy_client = MagicMock()
#     fake_srp_energy_client.usage.return_value = [{1, 2, 3, 1.999, 4}]
#     fake_config = MagicMock(
#         data={
#             "name": "SRP Energy",
#             "is_tou": False,
#             "id": "0123456789",
#             "username": "testuser@example.com",
#             "password": "mypassword",
#         }
#     )

#     hass.data[DOMAIN] = fake_srp_energy_client

#     await async_setup_entry(hass, fake_config, fake_async_add_entities)


# async def test_async_setup_entry_timeout_error(
#     hass: HomeAssistant, init_integration: MockConfigEntry
# ):
#     """Test fetching usage data. Failed the first time because was too get response."""
#     fake_async_add_entities = MagicMock()
#     fake_srp_energy_client = MagicMock()
#     fake_srp_energy_client.usage.return_value = [{1, 2, 3, 1.999, 4}]
#     fake_config = MagicMock(
#         entry_id="testid",
#         data={
#             "name": "SRP Energy",
#             "is_tou": False,
#             "id": "0123456789",
#             "username": "testuser@example.com",
#             "password": "mypassword",
#         },
#     )
#     hass.data.setdefault(DOMAIN, {})
#     hass.data[DOMAIN][fake_config.entry_id] = fake_srp_energy_client
#     fake_srp_energy_client.usage.side_effect = TimeoutError()

#     await async_setup_entry(hass, fake_config, fake_async_add_entities)

#     assert fake_srp_energy_client.usage.call_count == 1

#     assert not fake_async_add_entities.call_args[0][0][
#         0
#     ].coordinator.last_update_success


# async def test_async_setup_entry_connect_error(hass):
#     """Test fetching usage data. Failed the first time because was too get response."""
#     fake_async_add_entities = MagicMock()
#     fake_srp_energy_client = MagicMock()
#     fake_srp_energy_client.usage.return_value = [{1, 2, 3, 1.999, 4}]
#     fake_config = MagicMock(
#         data={
#             "name": "SRP Energy",
#             "is_tou": False,
#             "id": "0123456789",
#             "username": "testuser@example.com",
#             "password": "mypassword",
#         }
#     )
#     hass.data.setdefault(DOMAIN, {})
#     hass.data[DOMAIN][fake_config.entry_id] = fake_srp_energy_client
#     fake_srp_energy_client.usage.side_effect = ValueError()

#     await async_setup_entry(hass, fake_config, fake_async_add_entities)
#     assert not fake_async_add_entities.call_args[0][0][
#         0
#     ].coordinator.last_update_success


# async def test_srp_entity(hass):
#     """Test the SrpEntity."""
#     fake_coordinator = MagicMock(data=1.99999999999)
#     fake_entry_unique_id = "fake_sensor"
#     srp_entity = SrpEntity(
#         coordinator=fake_coordinator, entry_unique_id=fake_entry_unique_id
#     )
#     srp_entity.hass = hass

#     assert srp_entity is not None
#     assert srp_entity.name == f"{DEFAULT_NAME} {SENSOR_NAME}"
#     assert srp_entity.unique_id == SENSOR_TYPE
#     assert srp_entity.state == "69.4"
#     assert srp_entity.unit_of_measurement == ENERGY_KILO_WATT_HOUR
#     assert srp_entity.icon == ICON
#     assert srp_entity.should_poll is False
#     assert srp_entity.extra_state_attributes[ATTR_ATTRIBUTION] == ATTRIBUTION
#     assert srp_entity.available is not None
#     assert srp_entity.device_class is SensorDeviceClass.ENERGY
#     assert srp_entity.state_class is SensorStateClass.TOTAL_INCREASING

#     await srp_entity.async_added_to_hass()
#     assert srp_entity.state == "69.4"
#     assert fake_coordinator.async_add_listener.called
#     assert not fake_coordinator.async_add_listener.data.called


# async def test_srp_entity_no_coord_data(hass):
#     """Test the SrpEntity."""
#     fake_coordinator = MagicMock(data=False)
#     fake_entry_unique_id = "fake_sensor"
#     srp_entity = SrpEntity(fake_coordinator, fake_entry_unique_id)
#     srp_entity.hass = hass

#     assert srp_entity.state == "69.4"


# async def test_srp_entity_async_update(hass):
#     """Test the SrpEntity."""

#     async def async_magic():
#         pass

#     MagicMock.__await__ = lambda x: async_magic().__await__()
#     fake_coordinator = MagicMock(data=False)
#     fake_entry_unique_id = "fake_sensor"
#     srp_entity = SrpEntity(fake_coordinator, fake_entry_unique_id)
#     srp_entity.hass = hass

#     await srp_entity.async_update()
#     assert fake_coordinator.async_request_refresh.called
