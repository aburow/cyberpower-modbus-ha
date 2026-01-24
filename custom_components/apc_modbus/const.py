"""Constants for the APC UPS Modbus integration."""

from dataclasses import dataclass
from datetime import timedelta

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import STATE_CLASS_MEASUREMENT

from apc_modbus_registers import REGISTERS

DOMAIN = "apc_modbus"
DEFAULT_NAME = "APC UPS"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 10
DEFAULT_UNIT = 1
CONF_UNIT = "unit"

KEY_CLIENT = "modbus_client"
KEY_COORDINATOR = "coordinator"

SUPPORTED_PLATFORMS = ["sensor", "binary_sensor"]

@dataclass
class APCModbusSensorDescription(SensorEntityDescription):
    """Describe an APC Modbus sensor."""

    register_key: str = ""

@dataclass
class APCModbusBinarySensorDescription(BinarySensorEntityDescription):
    """Describe an APC Modbus binary sensor."""

    register_key: str = ""
    bit_index: int = 0

SENSOR_DESCRIPTIONS = [
    APCModbusSensorDescription(
        key="battery_state_of_charge",
        name="Battery State of Charge",
        native_unit_of_measurement="%",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="battery_state_of_charge",
    ),
    APCModbusSensorDescription(
        key="runtime_remaining",
        name="Runtime Remaining",
        native_unit_of_measurement="min",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="runtime_remaining",
    ),
    APCModbusSensorDescription(
        key="battery_voltage",
        name="Battery Voltage",
        native_unit_of_measurement="V",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="battery_voltage",
    ),
    APCModbusSensorDescription(
        key="battery_current",
        name="Battery Current",
        native_unit_of_measurement="A",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="battery_current",
    ),
    APCModbusSensorDescription(
        key="load_amps",
        name="Load Current",
        native_unit_of_measurement="A",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="load_amps",
    ),
    APCModbusSensorDescription(
        key="input_voltage",
        name="Input Voltage",
        native_unit_of_measurement="V",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="input_voltage",
    ),
    APCModbusSensorDescription(
        key="input_frequency",
        name="Input Frequency",
        native_unit_of_measurement="Hz",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="input_frequency",
    ),
    APCModbusSensorDescription(
        key="actual_output_voltage",
        name="Output Voltage",
        native_unit_of_measurement="V",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="actual_output_voltage",
    ),
    APCModbusSensorDescription(
        key="ups_id",
        name="UPS ID",
        register_key="ups_id",
        state_class=None,
    ),
]

BINARY_SENSOR_DESCRIPTIONS = [
    APCModbusBinarySensorDescription(
        key="ups_online",
        name="UPS Online",
        device_class=BinarySensorDeviceClass.POWER,
        register_key="status_word_3",
        bit_index=3,
    ),
    APCModbusBinarySensorDescription(
        key="ups_on_battery",
        name="UPS On Battery",
        device_class=BinarySensorDeviceClass.POWER,
        register_key="status_word_3",
        bit_index=4,
    ),
    APCModbusBinarySensorDescription(
        key="ups_overload",
        name="UPS Overload",
        device_class=BinarySensorDeviceClass.PROBLEM,
        register_key="status_word_3",
        bit_index=5,
    ),
    APCModbusBinarySensorDescription(
        key="ups_low_battery",
        name="UPS Low Battery",
        device_class=BinarySensorDeviceClass.BATTERY,
        register_key="status_word_3",
        bit_index=6,
    ),
    APCModbusBinarySensorDescription(
        key="ups_replace_battery",
        name="UPS Replace Battery",
        device_class=BinarySensorDeviceClass.BATTERY,
        register_key="status_word_3",
        bit_index=7,
    ),
]

SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
