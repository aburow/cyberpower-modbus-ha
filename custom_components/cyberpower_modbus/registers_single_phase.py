# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/cyberpower-modbus-ha

"""Register definitions for CyberPower single-phase UPS devices."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorStateClass

from .const import (
    CyberPowerModbusBinarySensorDescription,
    CyberPowerModbusSensorDescription,
)

REGISTERS = [
    # Status registers
    {
        "key": "hardware_fault",
        "address": 0x2000,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "utility_frequency_out_of_range",
        "address": 0x2008,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "inverter_off",
        "address": 0x2009,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "battery_not_present",
        "address": 0x200E,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "battery_discharging",
        "address": 0x2011,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "battery_charging",
        "address": 0x2012,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "battery_fully_charged",
        "address": 0x2014,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "buzzer_muted",
        "address": 0x2020,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "runtime_low",
        "address": 0x2021,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "no_output",
        "address": 0x2022,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "over_temperature",
        "address": 0x229C,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    # Measurements
    {
        "key": "utility_voltage",
        "address": 0x3000,
        "count": 1,
        "type": "uint16",
        "scale": 10,
    },
    {
        "key": "utility_frequency",
        "address": 0x3001,
        "count": 1,
        "type": "uint16",
        "scale": 10,
    },
    {
        "key": "output_voltage",
        "address": 0x3020,
        "count": 1,
        "type": "uint16",
        "scale": 10,
    },
    {
        "key": "output_load_percent",
        "address": 0x3027,
        "count": 1,
        "type": "uint16",
        "scale": 10,
    },
    {
        "key": "battery_capacity",
        "address": 0x3082,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "runtime_remaining",
        "address": 0x3083,
        "count": 2,
        "type": "uint32",
        "scale": 10,
        "word_order": "little",
    },
    {
        "key": "battery_threshold",
        "address": 0x3093,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "runtime_threshold",
        "address": 0x3094,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
]

REGISTER_BLOCKS = [
    {
        "name": "status",
        "start_address": 0x2000,
        "count": 0x23,
        "registers": [
            0x2000,
            0x2008,
            0x2009,
            0x200E,
            0x2011,
            0x2012,
            0x2014,
            0x2020,
            0x2021,
            0x2022,
        ],
    },
    {
        "name": "temperature_fault",
        "start_address": 0x229C,
        "count": 1,
        "registers": [0x229C],
    },
    {
        "name": "measurements_primary",
        "start_address": 0x3000,
        "count": 0x28,
        "registers": [
            0x3000,
            0x3001,
            0x3020,
            0x3027,
        ],
    },
    {
        "name": "measurements_battery",
        "start_address": 0x3082,
        "count": 0x13,
        "registers": [
            0x3082,
            0x3083,
            0x3093,
            0x3094,
        ],
    },
]

REGISTER_MAP = {reg["address"]: reg for reg in REGISTERS}


def get_sensor_descriptions() -> list[CyberPowerModbusSensorDescription]:
    """Return sensor descriptions for single-phase devices."""
    return [
        CyberPowerModbusSensorDescription(
            key="utility_voltage",
            name="Utility Voltage",
            native_unit_of_measurement="V",
            state_class=SensorStateClass.MEASUREMENT,
            register_key="utility_voltage",
        ),
        CyberPowerModbusSensorDescription(
            key="utility_frequency",
            name="Utility Frequency",
            native_unit_of_measurement="Hz",
            state_class=SensorStateClass.MEASUREMENT,
            register_key="utility_frequency",
        ),
        CyberPowerModbusSensorDescription(
            key="output_voltage",
            name="Output Voltage",
            native_unit_of_measurement="V",
            state_class=SensorStateClass.MEASUREMENT,
            register_key="output_voltage",
        ),
        CyberPowerModbusSensorDescription(
            key="output_load_percent",
            name="Output Load",
            native_unit_of_measurement="%",
            state_class=SensorStateClass.MEASUREMENT,
            register_key="output_load_percent",
        ),
        CyberPowerModbusSensorDescription(
            key="battery_capacity",
            name="Battery Capacity",
            native_unit_of_measurement="%",
            state_class=SensorStateClass.MEASUREMENT,
            register_key="battery_capacity",
        ),
        CyberPowerModbusSensorDescription(
            key="runtime_remaining",
            name="Runtime Remaining",
            native_unit_of_measurement="min",
            state_class=SensorStateClass.MEASUREMENT,
            register_key="runtime_remaining",
        ),
        CyberPowerModbusSensorDescription(
            key="battery_threshold",
            name="Battery Threshold",
            native_unit_of_measurement="%",
            state_class=SensorStateClass.MEASUREMENT,
            register_key="battery_threshold",
        ),
        CyberPowerModbusSensorDescription(
            key="runtime_threshold",
            name="Runtime Threshold",
            native_unit_of_measurement="s",
            state_class=SensorStateClass.MEASUREMENT,
            register_key="runtime_threshold",
        ),
    ]


def get_binary_sensor_descriptions() -> list[CyberPowerModbusBinarySensorDescription]:
    """Return binary sensor descriptions for single-phase devices."""
    return [
        CyberPowerModbusBinarySensorDescription(
            key="hardware_fault",
            name="Hardware Fault",
            device_class=BinarySensorDeviceClass.PROBLEM,
            register_key="hardware_fault",
        ),
        CyberPowerModbusBinarySensorDescription(
            key="utility_frequency_out_of_range",
            name="Utility Frequency Out of Range",
            device_class=BinarySensorDeviceClass.PROBLEM,
            register_key="utility_frequency_out_of_range",
        ),
        CyberPowerModbusBinarySensorDescription(
            key="inverter_off",
            name="Inverter Off",
            device_class=BinarySensorDeviceClass.PROBLEM,
            register_key="inverter_off",
        ),
        CyberPowerModbusBinarySensorDescription(
            key="battery_not_present",
            name="Battery Not Present",
            device_class=BinarySensorDeviceClass.PROBLEM,
            register_key="battery_not_present",
        ),
        CyberPowerModbusBinarySensorDescription(
            key="battery_discharging",
            name="Battery Discharging",
            device_class=BinarySensorDeviceClass.BATTERY,
            register_key="battery_discharging",
        ),
        CyberPowerModbusBinarySensorDescription(
            key="battery_charging",
            name="Battery Charging",
            device_class=BinarySensorDeviceClass.BATTERY,
            register_key="battery_charging",
        ),
        CyberPowerModbusBinarySensorDescription(
            key="battery_fully_charged",
            name="Battery Fully Charged",
            device_class=BinarySensorDeviceClass.BATTERY,
            register_key="battery_fully_charged",
        ),
        CyberPowerModbusBinarySensorDescription(
            key="buzzer_muted",
            name="Buzzer Muted",
            register_key="buzzer_muted",
        ),
        CyberPowerModbusBinarySensorDescription(
            key="runtime_low",
            name="Runtime Low",
            device_class=BinarySensorDeviceClass.BATTERY,
            register_key="runtime_low",
        ),
        CyberPowerModbusBinarySensorDescription(
            key="no_output",
            name="No Output",
            device_class=BinarySensorDeviceClass.PROBLEM,
            register_key="no_output",
        ),
        CyberPowerModbusBinarySensorDescription(
            key="over_temperature",
            name="Over Temperature",
            device_class=BinarySensorDeviceClass.PROBLEM,
            register_key="over_temperature",
        ),
    ]
