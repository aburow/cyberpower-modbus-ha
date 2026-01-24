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
    APCModbusSensorDescription(
        key="firmware_version",
        name="Firmware Version",
        register_key="firmware_version",
        state_class=None,
    ),
    APCModbusSensorDescription(
        key="model_name",
        name="Model Name",
        register_key="model_name",
        state_class=None,
    ),
    APCModbusSensorDescription(
        key="sku_name",
        name="SKU",
        register_key="sku_name",
        state_class=None,
    ),
    APCModbusSensorDescription(
        key="serial_number",
        name="Serial Number",
        register_key="serial_number",
        state_class=None,
    ),
    APCModbusSensorDescription(
        key="battery_install_date",
        name="Battery Installation Date",
        native_unit_of_measurement="days",
        state_class=STATE_CLASS_MEASUREMENT,
        register_key="battery_install_date",
    ),
    APCModbusSensorDescription(
        key="ups_name",
        name="UPS Name",
        register_key="ups_name",
        state_class=None,
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
