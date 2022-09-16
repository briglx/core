"""Constants for the SRP Energy integration."""
from datetime import timedelta
import logging
from typing import Final

LOGGER = logging.getLogger(__package__)

DOMAIN = "srp_energy"
DEFAULT_NAME = "SRP Energy"
CONF_IS_TOU = "is_tou"

ATTRIBUTION = "Powered by SRP Energy"
PHOENIX_TIME_ZONE = "America/Phoenix"
TIME_DELTA_BETWEEN_API_UPDATES = timedelta(hours=8)
TIME_DELTA_BETWEEN_UPDATES = timedelta(minutes=30)

DEVICE_NAME_ENERGY = "Energy consumption"
DEVICE_NAME_PRICE = "Energy consumption price"

DATA_SUMMARY_KEY_DAY: Final = "day"
DATA_SUMMARY_KEY_HOUR: Final = "hour"
DATA_SUMMARY_KEY_DATE: Final = "iso_date"
DATA_SUMMARY_KEY_VALUE: Final = "value"

DAILY_KEY_DATE_FORMAT = "%Y-%m-%dT00:00:00%z"
HOURLY_KEY_DATE_FORMAT = "%Y-%m-%dT%H:%M:00%z"

SENSOR_NAME = "Energy Usage"
