# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow <apburow@gmail.com>
# https://github.com/aburow/apc-modbus-snmp-ha

"""Shared register definitions for the APC UPS Modbus integration.

Based on 990-5702A-EN (Smart-UPS excluding SMT/SMX/SURTD/SRT).
Addresses are Modbus wire addresses (register number - 40000 for holding registers).
"""

REGISTERS = [
    # Status Words
    {
        "key": "status_word_0",
        "address": 0x0000,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "status_word_1",
        "address": 0x0001,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "status_word_2",
        "address": 0x0002,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "status_word_3",
        "address": 0x0003,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    # Line Quality & Battery
    {
        "key": "line_quality",
        "address": 0x0004,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "battery_state_of_charge",
        "address": 0x0005,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "runtime_remaining",
        "address": 0x0006,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "battery_voltage",
        "address": 0x0007,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    # Temperature & Load
    {
        "key": "ups_internal_temperature",
        "address": 0x0008,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "load_amps",
        "address": 0x0009,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "bad_battery_packs",
        "address": 0x000A,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "total_battery_packs",
        "address": 0x000B,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "load_percent",
        "address": 0x000C,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    # Output Voltage
    {
        "key": "nominal_output_voltage",
        "address": 0x000D,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "actual_output_voltage",
        "address": 0x000E,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    # Input Voltage & Frequency
    {
        "key": "max_input_voltage",
        "address": 0x000F,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "min_input_voltage",
        "address": 0x0010,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "input_voltage",
        "address": 0x0011,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "input_frequency",
        "address": 0x0012,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    # Environmental Probes (discontinued Measure-UPS)
    {
        "key": "measure_ups_temp_probe1",
        "address": 0x0013,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "measure_ups_humidity_probe1",
        "address": 0x0014,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "measure_ups_temp_probe2",
        "address": 0x0015,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "measure_ups_humidity_probe2",
        "address": 0x0016,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "measure_ups_contact_position",
        "address": 0x0017,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    # 0x0018-0x0019 (offsets 24-25) are Reserved and will fail per vendor spec
    # Battery Configuration
    {
        "key": "minimum_return_battery_capacity",
        "address": 0x001A,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "lower_transfer_point",
        "address": 0x001B,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "upper_transfer_point",
        "address": 0x001C,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "nominal_output_voltage_setting",
        "address": 0x001D,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "shutdown_delay",
        "address": 0x001E,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "low_battery_duration",
        "address": 0x001F,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "turn_on_delay",
        "address": 0x0020,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "sensitivity",
        "address": 0x0021,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    # UPS Identification (8 ASCII characters)
    {
        "key": "ups_id",
        "address": 0x0022,
        "count": 8,
        "type": "ascii",
        "scale": 1,
        "ascii_width": 1,
    },
    # Status Word 4 (extended faults)
    {
        "key": "status_word_4",
        "address": 0x002A,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    # Status Word 5 (extended faults)
    {
        "key": "status_word_5",
        "address": 0x002B,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    # Battery Voltage Information
    {
        "key": "nominal_battery_voltage",
        "address": 0x002C,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    {
        "key": "actual_battery_voltage",
        "address": 0x002D,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    # Three-phase specific (if applicable)
    {
        "key": "utility_input_voltage_phase_a",
        "address": 0x002E,
        "count": 1,
        "type": "uint16",
        "scale": 1,
    },
    # Battery Current (last valid register before reserved)
    {
        "key": "battery_current",
        "address": 0x004D,
        "count": 1,
        "type": "int16",
        "scale": 1,
    },
]

# Block read configuration for optimized polling
REGISTER_BLOCKS = [
    {
        "name": "status_battery_io",
        "start_address": 0x0000,
        "count": 24,
        "registers": [
            0x0000,
            0x0001,
            0x0002,
            0x0003,
            0x0004,
            0x0005,
            0x0006,
            0x0007,
            0x0008,
            0x0009,
            0x000A,
            0x000B,
            0x000C,
            0x000D,
            0x000E,
            0x000F,
            0x0010,
            0x0011,
            0x0012,
            0x0013,
            0x0014,
            0x0015,
            0x0016,
            0x0017,
        ],
    },
    {
        "name": "config_id_extended",
        "start_address": 0x001A,
        "count": 21,
        "registers": [
            0x001A,
            0x001B,
            0x001C,
            0x001D,
            0x001E,
            0x001F,
            0x0020,
            0x0021,
            0x0022,
            0x0023,
            0x0024,
            0x0025,
            0x0026,
            0x0027,
            0x0028,
            0x0029,
            0x002A,
            0x002B,
            0x002C,
            0x002D,
            0x002E,
        ],
    },
    {
        "name": "battery_current",
        "start_address": 0x004D,
        "count": 1,
        "registers": [0x004D],
    },
]

# Lookup map: address -> descriptor
REGISTER_MAP = {reg["address"]: reg for reg in REGISTERS}
