"""Constants for the APC UPS Modbus integration."""

from dataclasses import dataclass
from datetime import timedelta

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import STATE_CLASS_MEASUREMENT

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

REGISTERS = [
    {
        "key": "ups_status",
        "address": 0x0000,
        "count": 2,
        "type": "uint32",
        "scale": 1,
    },
    {
        "key": "ups_status_change",
        "address": 0x0002,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "general_error",
        "address": 0x0013,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "power_system_error",
        "address": 0x0014,
        "count": 2,
        "type": "uint32",
        "scale": 1,
    },
    {
        "key": "battery_system_error",
        "address": 0x0016,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "run_time_remaining",
        "address": 0x0080,
        "count": 2,
        "type": "uint32",
        "scale": 1,
    },
    {
        "key": "state_of_charge",
        "address": 0x0082,
        "count": 1,
        "type": "uint16",
        "scale": 512,
    },
    {
        "key": "battery_positive_voltage",
        "address": 0x0083,
        "count": 1,
        "type": "int16",
        "scale": 32,
    },
    {
        "key": "battery_negative_voltage",
        "address": 0x0084,
        "count": 1,
        "type": "int16",
        "scale": 32,
    },
    {
        "key": "battery_temperature",
        "address": 0x0087,
        "count": 1,
        "type": "int16",
        "scale": 128,
    },
    {
        "key": "output_frequency",
        "address": 0x0090,
        "count": 1,
        "type": "uint16",
        "scale": 128,
    },
    {
        "key": "output_voltage_phase_1",
        "address": 0x008C,
        "count": 1,
        "type": "uint16",
        "scale": 64,
    },
    {
        "key": "output_voltage_phase_2",
        "address": 0x008D,
        "count": 1,
        "type": "uint16",
        "scale": 64,
    },
]

SENSOR_DESCRIPTIONS = [
    APCModbusSensorDescription(
        key="run_time_remaining",
        name="Run Time Remaining",
        native_unit_of_measurement="s",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="run_time_remaining",
    ),
    APCModbusSensorDescription(
        key="state_of_charge",
        name="Battery State of Charge",
        native_unit_of_measurement="%",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="state_of_charge",
    ),
    APCModbusSensorDescription(
        key="battery_temperature",
        name="Battery Temperature",
        native_unit_of_measurement="°C",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="battery_temperature",
    ),
    APCModbusSensorDescription(
        key="output_frequency",
        name="Output Frequency",
        native_unit_of_measurement="Hz",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="output_frequency",
    ),
    APCModbusSensorDescription(
        key="output_voltage_phase_1",
        name="Output Voltage Phase 1",
        native_unit_of_measurement="V",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="output_voltage_phase_1",
    ),
]

BINARY_SENSOR_DESCRIPTIONS = [
    APCModbusBinarySensorDescription(
        key="ups_online",
        name="UPS Online",
        device_class=BinarySensorDeviceClass.POWER,
        register_key="ups_status",
        bit_index=1,
    ),
    APCModbusBinarySensorDescription(
        key="ups_on_battery",
        name="UPS On Battery",
        device_class=BinarySensorDeviceClass.POWER,
        register_key="ups_status",
        bit_index=2,
    ),
    APCModbusBinarySensorDescription(
        key="ups_fault",
        name="UPS Fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
        register_key="ups_status",
        bit_index=5,
    ),
]

SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
